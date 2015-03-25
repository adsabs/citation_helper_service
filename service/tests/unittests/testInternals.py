import sys, os
PROJECT_HOME = os.path.abspath(os.path.join(os.path.dirname(__file__),'../../'))
sys.path.append(PROJECT_HOME)
from flask.ext.testing import TestCase
from flask import request
from flask import url_for, Flask
import unittest
import requests
import time
import app
import json
import httpretty
from utils import get_data
from utils import get_meta_data

mockdata = [
    {'id':'1','bibcode':'a','title':['a_title'],'first_author':'a_author','reference':['x','z'],'citation':['p']},
    {'id':'2','bibcode':'b','title':['b_title'],'first_author':'b_author','reference':['d','x'],'citation':['p','c']},
    {'id':'3','bibcode':'c','title':['c_title'],'first_author':'c_author','reference':['e','y'],'citation':['p','y','a']},
    {'id':'4','bibcode':'x','title':['x_title'],'first_author':'x_author','reference':[],'citation':[]},
    {'id':'5','bibcode':'y','title':['y_title'],'first_author':'y_author','reference':[],'citation':[]},
    {'id':'6','bibcode':'z','title':['z_title'],'first_author':'z_author','reference':[],'citation':[]},
    {'id':'7','bibcode':'p','title':['p_title'],'first_author':'p_author','reference':[],'citation':[]}
    ]

class TestMethods(TestCase):
  '''Check if methods return expected results'''

  def create_app(self):
    '''Create the wsgi application'''
    app_ = app.create_app()
    return app_

  @httpretty.activate
  def test_service_results(self):
    '''Test to see if mock methods return expected results'''
    httpretty.register_uri(
            httpretty.GET, self.app.config.get('SOLRQUERY_URL'),
            content_type='application/json',
            status=200,
            body="""{
            "responseHeader":{
            "status":0, "QTime":0,
            "params":{ "fl":"reference,citation", "indent":"true", "wt":"json", "q":"*"}},
            "response":{"numFound":10456930,"start":0,"docs":%s
            }}"""%json.dumps(mockdata))

    expected_papers = [u'x', u'z', u'd', u'x', u'e', u'y', u'p', u'p', u'c', u'p', u'y', u'a']
    bibcodes = ['a','b','c']
    results = get_data(bibcodes=bibcodes)
    self.assertEqual(results, expected_papers)

    expected_meta = {u'a': {'author': u'a_author,+', 'title': u'a_title'}, 
                     u'c': {'author': u'c_author,+', 'title': u'c_title'}, 
                     u'b': {'author': u'b_author,+', 'title': u'b_title'}, 
                     u'p': {'author': u'p_author,+', 'title': u'p_title'}, 
                     u'y': {'author': u'y_author,+', 'title': u'y_title'}, 
                     u'x': {'author': u'x_author,+', 'title': u'x_title'}, 
                     u'z': {'author': u'z_author,+', 'title': u'z_title'}}
    scorelist = [('a',3),('b',2)]
    resmeta = get_meta_data(results=scorelist)
    self.assertEqual(resmeta, expected_meta)

if __name__ == '__main__':
  unittest.main()