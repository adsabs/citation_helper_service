'''
Created on Nov 1, 2014

@author: ehenneken
'''
from flask import current_app
from flask import request
import sys
import os
import urllib
import simplejson as json
from client import client


def get_data(**args):
    """
    Get the references for a set of bibcodes
    """
    references = []
    citations = []
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    # To restrict the size of the query URL, we split the list of
    # bibcodes up in a list of smaller lists
    biblists = list(
        chunks(args['bibcodes'],
               current_app.config.get('CITATION_HELPER_CHUNK_SIZE')))
    for biblist in biblists:
        q = " OR ".join(map(lambda a: "bibcode:%s" % a, biblist))
        # Get the information from Solr
        # We only need the contents of the 'reference' field (i.e. the
        # list of bibcodes referenced by the paper at hand)
        headers = {'X-Forwarded-Authorization':
                   request.headers.get('Authorization')}
        params = {'wt': 'json', 'q': q, 'fl': 'reference,citation',
                  'rows': current_app.config['CITATION_HELPER_MAX_HITS']}
        response = client().get(
            current_app.config.get('CITATION_HELPER_SOLR_PATH'),
            params=params, headers=headers)
        if response.status_code != 200:
            return {"Error": "Unable to get results!",
                    "Error Info": response.text,
                    "Status Code": response.status_code}
        resp = response.json()
        # Collect all bibcodes in a list (do NOT remove multiplicity)
        for doc in resp['response']['docs']:
            if 'reference' in doc:
                references += doc['reference']
            if 'citation' in doc:
                citations += doc['citation']
    return [bib for bib in references + citations]


def get_meta_data(**args):
    """
    Get the meta data for a set of bibcodes
    """
    data_dict = {}
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    bibcodes = [bibcode for (bibcode, score) in args['results']]
    list = " OR ".join(map(lambda a: "bibcode:%s" % a, bibcodes))
    q = '%s' % list
    # Get the information from Solr
    headers = {'X-Forwarded-Authorization':
               request.headers.get('Authorization')}
    params = {'wt': 'json', 'q': q, 'fl': 'bibcode,title,first_author',
              'rows': current_app.config.get('CITATION_HELPER_MAX_HITS')}
    response = client().get(
        current_app.config.get('CITATION_HELPER_SOLR_PATH'), params=params,
        headers=headers)
    if response.status_code != 200:
        return {"Error": "Unable to get results!",
                "Error Info": response.text,
                "Status Code": response.status_code}
    resp = response.json()
    # Collect meta data
    for doc in resp['response']['docs']:
        title = 'NA'
        if 'title' in doc:
            title = doc['title'][0]
        author = 'NA'
        if 'first_author' in doc:
            author = "%s et al." % doc['first_author']
        data_dict[doc['bibcode']] = {'title': title, 'author': author}
    return data_dict


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]
