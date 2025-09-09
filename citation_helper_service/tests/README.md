# Test data description
In order to test the Citation Helper algorithm, the following synthetic data is used. The table below summarizes the data

| Paper   |      Cites      |  isCitedBy |
|----------|:-------------:|:------:|
| a |  x, z | p|
| b |    d,x   |   p,c |
| c | e,y |    p,y,a |

The algorithm accumulates all publications cited by and citing the origin papers, keeping track of multiplicity. Next it removes all the publications from the original list and only keeps those with a multiplicity of at least 2 (the "score"). The end result is the following list

|Paper | Score |
|------|:-----:|
| p | 3 |
| y | 2|
| x | 2|

In the test implementation, mock data consists of a list of entries like

> {'id': '1', 'scix\_id': 'scix:a',
>      'identifier':['a', 'scix:a'],
>      'title': ['a_title'],
>      'first_author':'a_author',
>      'reference':['x', 'z'],
>      'citation':['p']}

The cited literature and citations in this mock data represent the data in the first table (above). This list of entries is returned as the mocked HTTP call to retrieve data from Solr. The `identifier` field in each of these entries contains both the paper identifier (read `bibcode`) and the associated SciX ID. The `title` and `first_author` entries are included to be used later to construct the final output. As a result, it should not matter whether the `reference` and `citation` fields contain bibcodes or SciX IDs, because to retrieve metadata, the `identifier` field is queried, which contains both.

With the results calculated above, the code should return the following

> {u'title': u'p_title', u'scix_id': u'scix:p', u'score': 3,
>                      u'author': u'p_author et al.'},
>                     {u'title': u'x_title', u'scix_id': u'scix:x',
>                         u'score': 2, u'author': u'x_author et al.'},
>                     {u'title': u'y_title', u'scix_id': u'scix:y', u'score': 2,
>                      u'author': u'y_author et al.'}
                     
This output should get returned whether the microservices receives `['a','b','c']` as initial input, or `['scix:a','scix:b','scix:c']` (representing the SciX ID equivalents). The one difference is, which is covered by a unit test, that when bibcodes are submitted to the service, the output contains bibcodes (rather than SciX IDs). Otherwise the service would have to maintain a mapping between the bibcodes and SciX IDs being processed and have logic to convert bibcodes into SciX IDs, when encountered.