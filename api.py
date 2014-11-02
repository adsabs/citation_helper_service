import sys
from flask import Flask
from flask import request
from flask import jsonify
from flask.ext.restful import abort, Api, Resource
from config import config
from citation_helper_utils import get_suggestions

app = Flask(__name__)
api = Api(app)

class CitationHelper(Resource):

    def post(self):
        if not request.json or not 'bibcodes' in request.json:
            abort(400)
        bibcodes = map(lambda a: str(a), request.json['bibcodes'])

        try:
            results = get_suggestions(bibcodes=bibcodes)
        except Exception, err:
            sys.stderr.write('Unable to get results! (%s)' % err)
            abort(400)

        return jsonify(suggestions=results)

class Resources(Resource):
    def get(self):
      return config.RESOURCES
##
## Actually setup the Api resource routing here
##
api.add_resource(CitationHelper, '/suggestions')
api.add_resource(Resources, '/resources')

if __name__ == '__main__':
    app.run(debug=True)
