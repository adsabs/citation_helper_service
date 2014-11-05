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
from utils import get_references
from utils import get_citing_papers
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
    Nsuggestions = current_app.config['NUMBER_SUGGESTIONS']
    # get rid of potential trailing spaces
    bibcodes = map(lambda a: a.strip(), bibcodes)[:current_app.config['MAX_INPUT']]
    # start processing
    # get the citations for all publications (keeping multiplicity is essential)
    cits = get_citing_papers(bibcodes=bibcodes)
    # clean up cits
    cits = filter(lambda a: len(a) > 0, cits)
    # get references
    refs = get_references(bibcodes=bibcodes)
    # clean up refs
    refs = filter(lambda a: len(a) > 0, refs)
    # removes papers from the original list to get candidates
    papers = filter(lambda a: a not in bibcodes, cits + refs)
    # establish frequencies of papers in results
    paperFreq = [(k,len(list(g))) for k, g in groupby(sorted(papers))]
    # and sort them, most frequent first
    paperFreq = sorted(paperFreq, key=operator.itemgetter(1),reverse=True)
    # remove all papers with frequencies smaller than threshold
    paperFreq = filter(lambda a: a[1] > current_app.config['THRESHOLD_FREQUENCY'], paperFreq)
    # get metadata for suggestions
    meta_dict = get_meta_data(results=paperFreq[:Nsuggestions])
    # return results in required format
    return [{'bibcode':x,'score':y, 'title':meta_dict[x]['title'], 'author':meta_dict[x]['author']} for (x,y) in paperFreq[:Nsuggestions] if x in meta_dict.keys()]
