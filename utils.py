'''
Created on Nov 1, 2014

@author: ehenneken
'''

# general module imports
import sys
import os
import time
from datetime import datetime
import operator
import glob
import requests
import urllib
from itertools import groupby
from multiprocessing import Process, Queue, cpu_count
import simplejson as json
from flask.ext.solrquery import solr 
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine

# local imports
from config import config

__all__ = ['get_citations','get_references','get_meta_data']

class PostgresQueryError(Exception):
    pass

class SolrReferenceQueryError(Exception):
    pass

class SolrMetaDataQueryError(Exception):
    pass

def solr_req(url, **kwargs):
    kwargs['wt'] = 'json'
    query_params = urllib.urlencode(kwargs)
    r = requests.get(url, params=query_params)
    return r.json()

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

Base = declarative_base()

class MetricsModel(Base):
  __tablename__='metrics'

  id = Column(Integer,primary_key=True)
  bibcode = Column(String,nullable=False,index=True)
  refereed = Column(Boolean)
  rn_citations = Column(postgresql.REAL)
  rn_citation_data = Column(postgresql.JSON)
  rn_citations_hist = Column(postgresql.JSON)
  downloads = Column(postgresql.ARRAY(Integer))
  reads = Column(postgresql.ARRAY(Integer))
  an_citations = Column(postgresql.REAL)
  refereed_citation_num = Column(Integer)
  citation_num = Column(Integer)
  citations = Column(postgresql.ARRAY(String))
  refereed_citations = Column(postgresql.ARRAY(String))
  author_num = Column(Integer)
  an_refereed_citations = Column(postgresql.REAL)
  modtime = Column(DateTime)

class CitationListHarvester(Process):
    """
    Class to allow parallel retrieval of citation data from Mongo
    """
    def __init__(self, task_queue, result_queue):
        Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(engine)
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()
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
            except PostgresQueryError, e:
                sys.stderr.write("Postgres metrics data query for %s blew up (%s)" % (bibcode,e))
                raise
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
    biblists = list(chunks(args['bibcodes'], config.CHUNK_SIZE))
    for biblist in biblists:
        q = " OR ".join(map(lambda a: "bibcode:%s"%a, biblist))
        try:
            # Get the information from Solr
            # We only need the contents of the 'reference' field (i.e. the list of bibcodes 
            # referenced by the paper at hand)
            resp = solr_req(config.SOLRQUERY_URL, q=q, fl = 'reference', rows=config.MAX_HITS)
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
        resp = solr_req(config.SOLRQUERY_URL, q=q, fl = 'bibcode,title,first_author', rows=config.MAX_HITS)
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
