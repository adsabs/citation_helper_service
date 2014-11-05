from flask import current_app, Blueprint, request
from flask.ext.restful import Resource
import time

from utils.citation_helper import get_suggestions

blueprint = Blueprint(
      'citation_helper',
      __name__,
      static_folder=None,
)

class CitationHelper(Resource):
    """computes Citation Helper suggestions on the POST body"""
    scopes = 'oauth:suggestions:read'
    def post(self):
        if not request.json or not 'bibcodes' in request.json:
            return {'msg': 'no bibcodes found in POST body'}, 400
        bibcodes = map(str, request.json['bibcodes'])
        if len(bibcodes) > current_app.config['MAX_SUBMITTED']:
            return {'msg': 'number of submitted bibcodes exceeds maximum number'}, 400
        try:
            results = get_suggestions(bibcodes=bibcodes)
        except Exception, err:
            return {'msg': 'Unable to get results! (%s)' % err}, 500

        return results

class Resources(Resource):
  '''Overview of available resources'''
  scopes = ['oauth:sample_application:read','oauth_sample_application:logged_in']
  def get(self):
    func_list = {}
    for rule in current_app.url_map.iter_rules():
      func_list[rule.rule] = {'methods':current_app.view_functions[rule.endpoint].methods,
                              'scopes': current_app.view_functions[rule.endpoint].view_class.scopes,
                              'description': current_app.view_functions[rule.endpoint].view_class.__doc__,
                              }
    return func_list, 200

class UnixTime(Resource):
  '''Returns the unix timestamp of the server'''
  scopes = ['oauth:sample_application:read','oauth_sample_application:logged_in']
  def get(self):
    return {'now': time.time()}, 200
