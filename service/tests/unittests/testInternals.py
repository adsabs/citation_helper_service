import sys
import os
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../'))
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
from utils import chunks

mockdata = [
    {'id': '1', 'bibcode': 'a',
     'title': ['a_title'],
     'first_author':'a_author',
     'reference':['x', 'z'],
     'citation':['p']},
    {'id': '2', 'bibcode': 'b',
     'title': ['b_title'],
     'first_author':'b_author',
     'reference':['d', 'x'],
     'citation':['p', 'c']},
    {'id': '3', 'bibcode': 'c',
     'title': ['c_title'],
     'first_author':'c_author',
     'reference':['e', 'y'],
     'citation':['p', 'y', 'a']},
    {'id': '4', 'bibcode': 'x',
     'title': ['x_title'],
     'first_author':'x_author',
     'reference':[],
     'citation':[]},
    {'id': '5', 'bibcode': 'y',
     'title': ['y_title'],
     'first_author':'y_author',
     'reference':[],
     'citation':[]},
    {'id': '6',
     'bibcode': 'z',
     'title': ['z_title'],
     'first_author':'z_author',
     'reference':[],
     'citation':[]},
    {'id': '7', 'bibcode': 'p',
     'title': ['p_title'],
     'first_author':'p_author',
     'reference':[],
     'citation':[]}
]


class TestConfig(TestCase):

    '''Check if config has necessary entries'''

    def create_app(self):
        '''Create the wsgi application'''
        app_ = app.create_app()
        return app_

    def test_config_values(self):
        '''Check if all required config variables are there'''
        required = ["CITATION_HELPER_MAX_HITS",
                    "CITATION_HELPER_MAX_INPUT",
                    "CITATION_HELPER_MAX_SUBMITTED",
                    "CITATION_HELPER_CHUNK_SIZE",
                    "CITATION_HELPER_NUMBER_SUGGESTIONS",
                    "CITATION_HELPER_THRESHOLD_FREQUENCY",
                    "CITATION_HELPER_SOLR_PATH",
                    "DISCOVERER_PUBLISH_ENDPOINT",
                    "DISCOVERER_SELF_PUBLISH"]
        missing = [x for x in required if x not in self.app.config.keys()]
        self.assertTrue(len(missing) == 0)
        # Check if API has an actual value
        if os.path.exists("%s/local_config.py" % PROJECT_HOME):
            self.assertTrue(
                self.app.config.get('CITATION_HELPER_API_TOKEN', None) != None)


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
            httpretty.GET, self.app.config.get(
                'CITATION_HELPER_SOLR_PATH'),
            content_type='application/json',
            status=200,
            body="""{
            "responseHeader":{
            "status":0, "QTime":0,
            "params":{ "fl":"reference,citation", "indent":"true",
            "wt":"json", "q":"*"}},
            "response":{"numFound":10456930,"start":0,"docs":%s
            }}""" % json.dumps(mockdata))

        expected_papers = [
            u'x', u'z', u'd', u'x', u'e', u'y', u'p',
            u'p', u'c', u'p', u'y', u'a']
        bibcodes = ['a', 'b', 'c']
        results = get_data(bibcodes=bibcodes)
        self.assertEqual(results, expected_papers)

        expected_meta = {u'a': {'author': u'a_author et al.', 'title': u'a_title'},
                         u'c': {'author': u'c_author et al.', 'title': u'c_title'},
                         u'b': {'author': u'b_author et al.', 'title': u'b_title'},
                         u'p': {'author': u'p_author et al.', 'title': u'p_title'},
                         u'y': {'author': u'y_author et al.', 'title': u'y_title'},
                         u'x': {'author': u'x_author et al.', 'title': u'x_title'},
                         u'z': {'author': u'z_author et al.', 'title': u'z_title'}}
        scorelist = [('a', 3), ('b', 2)]
        resmeta = get_meta_data(results=scorelist)
        self.assertEqual(resmeta, expected_meta)

    def test_chunks(self):
        '''Test if the chunks method behaves properly'''
        list = ['a', 'b', 'c', 'd']
        expected = [['a'], ['b'], ['c'], ['d']]
        self.assertEqual([x for x in chunks(list, 1)], expected)

if __name__ == '__main__':
    unittest.main()
