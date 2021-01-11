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
    bibcodes = []
    if 'bibcodes' in args:
        bibcodes = args['bibcodes']
    if len(bibcodes) == 0:
        return []
    # Any overrides for default values?
    Nsuggestions = current_app.config.get('CITATION_HELPER_NUMBER_SUGGESTIONS')
    # get rid of potential trailing spaces
    bibcodes = [a.strip() for a in bibcodes][
        :current_app.config.get('CITATION_HELPER_MAX_INPUT')]
    # start processing
    # get the citations for all publications (keeping multiplicity is
    # essential)
    papers = get_data(bibcodes=bibcodes)
    if "Error" in papers:
        return papers
    # removes papers from the original list to get candidates
    papers = [a for a in papers if a not in bibcodes]
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
    return [{'bibcode': x, 'score': y, 'title': meta_dict[x]['title'],
             'author':meta_dict[x]['author']} for (x, y) in
            paperFreq[:Nsuggestions] if x in list(meta_dict.keys())]
