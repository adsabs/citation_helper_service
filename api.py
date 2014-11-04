import sys
from flask import Flask
from flask import request
from flask import Blueprint
from flask.ext.restful import Api, Resource
from config import config
from citation_helper_utils import get_suggestions

app_blueprint = Blueprint('api', __name__)
api = Api(app_blueprint)

class CitationHelper(Resource):
    """computes Citation Helper suggestions on the POST body"""
    scope = 'oauth:suggestions:read'
    def post(self):
        if not request.json or not 'bibcodes' in request.json:
            return {'msg': 'no bibcodes found in POST body'}, 400
        bibcodes = map(lambda a: str(a), request.json['bibcodes'])

        try:
            results = get_suggestions(bibcodes=bibcodes)
        except Exception, err:
            return {'msg': 'Unable to get results! (%s)' % err}, 500

        return results

class Resources(Resource):
    """Overview of available resources"""
    scope = 'oauth:resources:read'
    def get(self):
        func_list = {}
        for rule in app.url_map.iter_rules():
            func_list[rule.rule] = {'methods':app.view_functions[rule.endpoint].methods,
                                    'scope': app.view_functions[rule.endpoint].view_class.scope,
                                    'description': app.view_functions[rule.endpoint].view_class.__doc__,
                                       }
        return func_list
##
## Actually setup the Api resource routing here
##
api.add_resource(CitationHelper, '/suggestions')
api.add_resource(Resources, '/resources')

if __name__ == '__main__':
    app = Flask(__name__, static_folder=None)
    app.register_blueprint(app_blueprint)
    app.run(debug=True)