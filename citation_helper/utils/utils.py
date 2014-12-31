'''
Created on Nov 1, 2014

@author: ehenneken
'''
from flask import current_app
import sys
import os
import urllib
from multiprocessing import Process, Queue, cpu_count
import simplejson as json
from database import db, AlchemyEncoder, MetricsModel

class PostgresQueryError(Exception):
    pass

class SolrReferenceQueryError(Exception):
    pass

class SolrMetaDataQueryError(Exception):
    pass

class CitationListHarvester(Process):
    """
    Class to allow parallel retrieval of citation data from PostgreSQL
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.session = db.session()
    def run(self):
        while True:
            bibcode = self.task_queue.get()
            if bibcode is None:
                break
            try:
                result = self.session.query(MetricsModel).filter(MetricsModel.bibcode==bibcode).one()
                try:
                    citations = result.citations
                except:
                    citations = []
                self.result_queue.put({'citations':citations})
            except:
                self.result_queue.put({'citations':[]})
        return

def get_citing_papers(**args):
    # create the queues
    tasks = Queue()
    results = Queue()
    # how many threads are there to be used
    if 'threads' in args:
        threads = args['threads']
    else:
        threads = cpu_count()
    bibcodes = args.get('bibcodes',[])
    # initialize the "harvesters" (each harvester get the citations for a bibcode)
    harvesters = [ CitationListHarvester(tasks, results) for i in range(threads)]
    # start the harvesters
    for b in harvesters:
        b.start()
    # put the bibcodes in the tasks queue
    num_jobs = 0
    for bib in bibcodes:
        tasks.put(bib)
        num_jobs += 1
    # add some 'None' values at the end of the tasks list, to faciliate proper closure
    for i in range(threads):
        tasks.put(None)
    # gather all results into one citation dictionary
    cit_list = []
    while num_jobs:
        data = results.get()
        if 'Exception' in data:
            raise PostgresQueryError, data
        cit_list += data.get('citations',[])
        num_jobs -= 1
    return cit_list

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
