'''
Created on Nov 1, 2014

@author: ehenneken
'''
from flask import current_app
import sys
import os
import urllib
import simplejson as json
from database import db, MetricsModel
from sqlalchemy import or_

class PostgresQueryError(Exception):
    pass

class SolrReferenceQueryError(Exception):
    pass

class SolrMetaDataQueryError(Exception):
    pass

def get_citing_papers(**args):
    bibcodes = args.get('bibcodes',[])
    querydata = []
    citlist = []
    for bibcode in bibcodes:
        querydata.append(MetricsModel.bibcode=='%s'%bibcode)
    condition = or_(*querydata)

    try:
        results = db.session.query(MetricsModel).filter(condition).all()
    except PostgresQueryError, e:
        sys.stderr.write("Postgres query blew up (%s)" % e)
        raise

    for result in results:
        try:
            citlist += result.citations
        except:
            continue
    return citlist

def get_references(**args):
    """
    Get the references for a set of bibcodes
    """
    papers= []
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    # To restrict the size of the query URL, we split the list of
    # bibcodes up in a list of smaller lists
    biblists = list(chunks(args['bibcodes'], current_app.config['CHUNK_SIZE']))
    for biblist in biblists:
        q = " OR ".join(map(lambda a: "bibcode:%s"%a, biblist))
        try:
            # Get the information from Solr
            # We only need the contents of the 'reference' field (i.e. the list of bibcodes 
            # referenced by the paper at hand)
            params = {'wt':'json', 'q':q, 'fl':'reference', 'rows': current_app.config['MAX_HITS']}
            query_url = current_app.config['SOLRQUERY_URL'] + "/?" + urllib.urlencode(params)
            resp = current_app.client.session.get(query_url).json()
        except SolrReferenceQueryError, e:
            sys.stderr.write("Solr references query for %s blew up (%s)" % (q,e))
            raise
        # Collect all bibcodes in a list (do NOT remove multiplicity)
        for doc in resp['response']['docs']:
            if 'reference' in doc:
                papers += doc['reference']
    return papers

def get_meta_data(**args):
    """
    Get the meta data for a set of bibcodes
    """
    data_dict = {}
    # This information can be retrieved with one single Solr query
    # (just an 'OR' query of a list of bibcodes)
    bibcodes = [bibcode for (bibcode,score) in args['results']]
    list = " OR ".join(map(lambda a: "bibcode:%s"%a, bibcodes))
    q = '%s' % list
    try:
        # Get the information from Solr
        params = {'wt':'json', 'q':q, 'fl':'bibcode,title,first_author', 'rows': current_app.config['MAX_HITS']}
        query_url = current_app.config['SOLRQUERY_URL'] + "/?" + urllib.urlencode(params)
        resp = current_app.client.session.get(query_url).json()
    except SolrMetaDataQueryError, e:
        sys.stderr.write("Solr references query for %s blew up (%s)" % (bibcode,e))
        raise
    # Collect meta data
    for doc in resp['response']['docs']:
        title = 'NA'
        if 'title' in doc: title = doc['title'][0]
        author = 'NA'
        if 'first_author' in doc: author = "%s,+"%doc['first_author'].split(',')[0]
        data_dict[doc['bibcode']] = {'title':title, 'author':author}
    return data_dict

def chunks(l, n):
    """ 
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]
