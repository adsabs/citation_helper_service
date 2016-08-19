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


class TestBadRequests(TestCase):

    '''Tests that no or too many submitted bibcodes result
       in the proper responses'''

    def create_app(self):
        '''Create the wsgi application'''
        app_ = app.create_app()
        return app_

    def testNoBibcodesSubmitted(self):
        '''When no input bibcodes are submitted an error should be raised'''
        r = self.client.post(
            url_for('citationhelper'),
            data=dict(bibcodes=[]))
        self.assertTrue(r.status_code == 200)
        self.assertTrue('Error' in r.json)
        self.assertTrue(r.json.get('Error') == 'Unable to get results!')

    def testTooManyBibcodes(self):
        '''When more than the maximum input bibcodes are submitted an error
           should be raised'''
        bibcodes = ["bibcode"] * \
            (self.app.config.get('CITATION_HELPER_MAX_SUBMITTED') + 1)
        r = self.client.post(
            url_for('citationhelper'),
            content_type='application/json',
            data=json.dumps({'bibcodes': bibcodes}))
        self.assertTrue(r.status_code == 200)
        self.assertTrue('Error' in r.json)
        self.assertTrue(r.json.get('Error') == 'Unable to get results!')


class TestGoodRequests(TestCase):

    '''Tests for when non-trivial results are expected'''

    def create_app(self):
        '''Create the wsgi application'''
        app_ = app.create_app()
        return app_

    @httpretty.activate
    def test_service_results(self):
        '''Test to see if mock data produces expected results'''
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

        expected = [{u'title': u'p_title', u'bibcode': u'p', u'score': 3,
                     u'author': u'p_author,+'},
                    {u'title': u'x_title', u'bibcode': u'x',
                        u'score': 2, u'author': u'x_author,+'},
                    {u'title': u'y_title', u'bibcode': u'y', u'score': 2,
                     u'author': u'y_author,+'}]

        bibcodes = ['a', 'b', 'c']

        r = self.client.post(
            url_for('citationhelper'),
            content_type='application/json',
            data=json.dumps({'bibcodes': bibcodes}))

        self.assertTrue(r.status_code == 200)
        self.assertEqual(expected, r.json)


class TestSolrError(TestCase):

    '''Tests for when Solr request gives bad status back'''

    def create_app(self):
        '''Create the wsgi application'''
        app_ = app.create_app()
        return app_

    @httpretty.activate
    def test_service_results(self):
        '''Tests for when Solr request gives bad status back'''
        httpretty.register_uri(
            httpretty.GET, self.app.config.get(
                'CITATION_HELPER_SOLR_PATH'),
            content_type='application/json',
            status=500,
            body="""{
            "responseHeader":{
            "status":0, "QTime":0,
            "params":{ "fl":"reference,citation", "indent":"true",
            "wt":"json", "q":"*"}},
            "response":{"numFound":10456930,"start":0,"docs":[]
            }}""")

        bibcodes = ['a', 'b', 'c']

        r = self.client.post(
            url_for('citationhelper'),
            content_type='application/json',
            data=json.dumps({'bibcodes': bibcodes}))

        self.assertTrue(r.status_code == 200)
        self.assertTrue('Error' in r.json)
        self.assertTrue('Unable to get results' in r.json.get('Error'))


class TestNoRequests(TestCase):

    '''Tests for when no results are expected'''

    def create_app(self):
        '''Create the wsgi application'''
        app_ = app.create_app()
        return app_

    @httpretty.activate
    def test_service_results(self):
        '''Tests for when no results are expected'''
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
            "response":{"numFound":0,"start":0,"docs":[]
            }}""")

        bibcodes = ['a', 'b', 'c']

        r = self.client.post(
            url_for('citationhelper'),
            content_type='application/json',
            data=json.dumps({'bibcodes': bibcodes}))

        self.assertTrue(r.status_code == 200)
        self.assertTrue('Error' in r.json)
        self.assertTrue(r.json.get('Error') == 'Unable to get results!')

if __name__ == '__main__':
    unittest.main()
