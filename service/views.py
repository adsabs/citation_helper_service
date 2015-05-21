from flask import current_app, request
from flask.ext.restful import Resource
from flask.ext.discoverer import advertise
from citation_helper import get_suggestions


class CitationHelper(Resource):

    """computes Citation Helper suggestions on the POST body"""
    scopes = []
    rate_limit = [1000, 60 * 60 * 24]
    decorators = [advertise('scopes', 'rate_limit')]

    def post(self):
        if not request.json or 'bibcodes' not in request.json:
            return {'Error': 'Unable to get results!',
                    'Error Info': 'No bibcodes found in POST body'}, 200
        bibcodes = map(str, request.json['bibcodes'])
        if len(bibcodes) > \
                current_app.config.get('CITATION_HELPER_MAX_SUBMITTED'):
            return {'Error': 'Unable to get results!',
                    'Error Info':
                    'Number of submitted bibcodes exceeds maximum number'}, 200

        results = get_suggestions(bibcodes=bibcodes)
        if "Error" in results:
            return results, 500

        if results:
            return results
        else:
            return {'Error': 'Unable to get results!',
                    'Error Info': 'Could not find anything to suggest'}, 200
