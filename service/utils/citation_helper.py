'''
Created on Nov 1, 2014

@author: ehenneken
'''

# general module imports
import sys
import os
import operator
from itertools import groupby
from flask import current_app
from utils import get_data
from utils import get_meta_data
 
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
    bibcodes = map(lambda a: a.strip(), bibcodes)[:current_app.config.get('CITATION_HELPER_MAX_INPUT')]
    # start processing
    # get the citations for all publications (keeping multiplicity is essential)
    papers = get_data(bibcodes=bibcodes)
    if "Error" in papers:
        return papers
    # removes papers from the original list to get candidates
    papers = filter(lambda a: a not in bibcodes, papers)
    # establish frequencies of papers in results
    paperFreq = [(k,len(list(g))) for k, g in groupby(sorted(papers))]
    # and sort them, most frequent first
    paperFreq = sorted(paperFreq, key=operator.itemgetter(1),reverse=True)
    # remove all papers with frequencies smaller than threshold
    paperFreq = filter(lambda a: a[1] > current_app.config.get('CITATION_HELPER_THRESHOLD_FREQUENCY'), paperFreq)
    # get metadata for suggestions
    meta_dict = get_meta_data(results=paperFreq[:Nsuggestions])
    if "Error"in meta_dict:
        return meta_dict
    # return results in required format
    return [{'bibcode':x,'score':y, 'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for (x,y) in paperFreq[:Nsuggestions] if x in meta_dict.keys()]
