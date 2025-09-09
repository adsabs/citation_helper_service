'''
Created on Nov 1, 2014

@author: ehenneken
'''
from __future__ import absolute_import

# general module imports
import sys
import os
import operator
from itertools import groupby
from flask import current_app
from .utils import get_data
from .utils import get_meta_data

__all__ = ['get_suggestions']


def get_suggestions(**args):
    # initializations
    papers = []
    identifiers = []
    if 'identifiers' in args:
        identifiers = args['identifiers']
    if len(identifiers) == 0:
        return []
    # Any overrides for default values?
    Nsuggestions = current_app.config.get('CITATION_HELPER_NUMBER_SUGGESTIONS')
    # get rid of potential trailing spaces
    identifiers = [a.strip() for a in identifiers][
        :current_app.config.get('CITATION_HELPER_MAX_INPUT')]
    # start processing
    # get the citations for all publications (keeping multiplicity is
    # essential)
    papers = get_data(identifiers=identifiers)
    if "Error" in papers:
        return papers
    # removes papers from the original list to get candidates
    papers = [a for a in papers if a not in identifiers]
    # establish frequencies of papers in results
    paperFreq = [(k, len(list(g))) for k, g in groupby(sorted(papers))]
    # and sort them, most frequent first
    paperFreq = sorted(paperFreq, key=operator.itemgetter(1), reverse=True)
    # remove all papers with frequencies smaller than threshold
    paperFreq = [a for a in paperFreq if a[1] > current_app.config.get(
        'CITATION_HELPER_THRESHOLD_FREQUENCY')]
    # get metadata for suggestions
    meta_dict = get_meta_data(results=paperFreq[:Nsuggestions])
    if "Error"in meta_dict:
        return meta_dict
    # return results in required format
    # Here we need to distinguish between whether the service received bibcodes
    # or SciX IDs as input. Unless we convert bibcodes into SciX IDs in the very beginning
    # (in the first case). In the future, we will be calling this service with just SciX IDs;
    # at that point it will be less work to clean up this little conditional data processing
    # than cleaning up all the logic to replace bibcodes by SciX IDs.
    results = []
    for p, s in paperFreq[:Nsuggestions]:
        if p.startswith('scix:') and p in meta_dict:
            results.append({'scix_id': p, 'score': s, 'title': meta_dict[p]['title'],
             'author':meta_dict[p]['author']})
        elif p in meta_dict:
            results.append({'bibcode': p, 'score': s, 'title': meta_dict[p]['title'],
             'author':meta_dict[p]['author']})
    return results
