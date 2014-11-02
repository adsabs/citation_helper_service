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
    METRICS_DEFAULT_MODELS = 'statistics,histograms,metrics,series'
    THRESHOLD_FREQUENCY = 1
    SOLRQUERY_URL = 'http://adswhy:9000/solr/collection1/select'
    SOLRQUERY_TIMEOUT = 300
    SOLRQUERY_KEEPALIVE = False
    SOLRQUERY_HTTP_METHOD = 'POST'
    SOLRQUERY_EXTRA_PARAMS = [
        ('hl.maxAnalyzedChars', '150000'),
        ('hl.requireFieldMatch', 'true'),
        ('hl.usePhraseHighlighter', 'true'),
        ('indent', 'true')
    ]

    SOLR_DOCUMENT_ID_FIELD = 'bibcode'
    SOLR_FILTER_QUERY_PARSER = 'aqp'
    SOLR_HIGHLIGHTER_QUERY_PARSER = 'aqp'
    SOLR_HAPROXY_SESSION_COOKIE_NAME = 'JSESSIONID'

    
try:
    from local_config import LocalConfig
except ImportError:
    LocalConfig = type('LocalConfig', (object,), dict())
    
for attr in filter(lambda x: not x.startswith('__'), dir(LocalConfig)):
    setattr(AppConfig, attr, LocalConfig.__dict__[attr])
    
config = AppConfig
