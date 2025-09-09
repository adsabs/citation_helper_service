'''
Created on Nov 1, 2014

@author: ehenneken
'''
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from builtins import range
from flask import current_app
from flask import request
import sys
import os
import urllib.request, urllib.parse, urllib.error
import simplejson as json
from .client import Client


def get_data(**args):
    """
    Get the references for a set of identifiers
    """
    references = []
    citations = []
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of identifiers)
    # To restrict the size of the query URL, we split the list of
    # identifiers up in a list of smaller lists
    idlists = list(
        chunks(args['identifiers'],
               current_app.config.get('CITATION_HELPER_CHUNK_SIZE')))
    for idlist in idlists:
        q = " OR ".join(['identifier:"%s"' % a for a in idlist])
        # Get the information from Solr
        # We only need the contents of the 'reference' field (i.e. the
        # list of identifiers referenced by the paper at hand)
        params = {'wt': 'json', 'q': q, 'fl': 'reference,citation',
                  'rows': current_app.config['CITATION_HELPER_MAX_HITS']}
        response = Client(config=current_app.config).get(
            current_app.config.get('CITATION_HELPER_SOLR_PATH'),
            params=params)
        if response.status_code != 200:
            return {"Error": "Unable to get citation lists!",
                    "Error Info": "Solr response: %s" % str(response.text),
                    "Status Code": response.status_code}
        resp = response.json()
        # Collect all identifiers in a list (do NOT remove multiplicity)
        for doc in resp['response']['docs']:
            if 'reference' in doc:
                references += doc['reference']
            if 'citation' in doc:
                citations += doc['citation']
    return [identifier for identifier in references + citations]


def get_meta_data(**args):
    """
    Get the meta data for a set of identifiers
    """
    data_dict = {}
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of identifiers)
    identifiers = [identifier for (identifier, score) in args['results']]
    qlist = " OR ".join(['identifier:"%s"' % a for a in identifiers])
    q = '%s' % qlist
    # Get the information from Solr
    params = {'wt': 'json', 'q': q, 'fl': 'scix_id,bibcode,title,first_author',
              'rows': current_app.config.get('CITATION_HELPER_MAX_HITS')}
    response = Client(config=current_app.config).get(
        current_app.config.get('CITATION_HELPER_SOLR_PATH'), params=params
        )
    if response.status_code != 200:
        return {"Error": "Unable to get metadata!",
                "Error Info": response.text,
                "Status Code": response.status_code}
    resp = response.json()
    # Collect meta data
    # The logic to add a "bibcode" entry in there is to support
    # the cases where the service is called with bibcodes
    for doc in resp['response']['docs']:
        title = 'NA'
        if 'title' in doc:
            title = doc['title'][0]
        author = 'NA'
        if 'first_author' in doc:
            author = "%s et al." % doc['first_author']
        bibcode = 'NA'
        if 'bibcode' in doc:
            bibcode = doc['bibcode']
        data_dict[doc['scix_id']] = {'title': title, 'author': author}
        if bibcode != 'NA':
            data_dict[bibcode] = {'title': title, 'author': author}
    return data_dict

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]
