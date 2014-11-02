import os

_basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

APP_NAME = "suggestions"

class AppConfig(object):
    RESOURCES = [
                    {
                        '/suggestions/': {
                            'allowed': ['POST',],
                            'scope': 'oauth:suggestions:read', #this is an arbitrary string, and adsws will take care of this, but this lets each app decide which permissions adsws should enforce
                            'description': 'computes Citation Helper suggestions on the POST body',
                            }
                    },
                    {
                        '/resources': {
                            'allowed':['GET',],
                            'scope':'oauth:resources:read',
                            'description': 'Get this overview',
                            }
                    },
                ]
    MAX_HITS = 10000    
    MAX_INPUT = 500
    CHUNK_SIZE = 100
    NUMBER_SUGGESTIONS = 10
    SQLALCHEMY_DATABASE_URI = ''
    THRESHOLD_FREQUENCY = 1
    SOLRQUERY_URL = 'http://adswhy:9000/solr/collection1/select'
    
try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])
    
config = AppConfig
