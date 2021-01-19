from __future__ import absolute_import
from builtins import map
from builtins import str
from flask import current_app, request
from flask_restful import Resource
from flask_discoverer import advertise
from .citation_helper import get_suggestions
import time


class CitationHelper(Resource):

    """computes Citation Helper suggestions on the POST body"""
    scopes = []
    rate_limit = [1000, 60 * 60 * 24]
    decorators = [advertise('scopes', 'rate_limit')]

    def post(self):
        stime = time.time()
        if not request.json or 'bibcodes' not in request.json:
            current_app.logger.error('No bibcodes were provided to Citation Helper')
            return {'Error': 'Unable to get results!',
                    'Error Info': 'No bibcodes found in POST body'}, 200
        bibcodes = list(map(str, request.json['bibcodes']))
        if len(bibcodes) > \
                current_app.config.get('CITATION_HELPER_MAX_SUBMITTED'):
            current_app.logger.warning('Citation Helper called with %s bibcodes. Maximum is: %s!'%(len(bibcodes),current_app.config.get('CITATION_HELPER_MAX_SUBMITTED')))
            return {'Error': 'Unable to get results!',
                    'Error Info':
                    'Number of submitted bibcodes exceeds maximum number'}, 200

        results = get_suggestions(bibcodes=bibcodes)
        if "Error" in results:
            msg = 'Citation Helper request request blew up'
            if 'Error Info' in results:
                msg += ' (%s)' % str(results['Error Info'])
            current_app.logger.error(msg)
            return results, 200

        if results:
            duration = time.time() - stime
            current_app.logger.info('Citation Helper request successfully completed in %s real seconds'%duration)
            return results
        else:
            current_app.logger.info('Citation Helper request returned empty result')
            return {'Error': 'Unable to get results!',
                    'Error Info': 'Could not find anything to suggest'}, 200
