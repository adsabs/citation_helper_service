CITATION_HELPER_SECRET_KEY = 'this should be changed'
CITATION_HELPER_MAX_HITS = 10000
CITATION_HELPER_MAX_INPUT = 500
CITATION_HELPER_MAX_SUBMITTED = 100
CITATION_HELPER_CHUNK_SIZE = 100
CITATION_HELPER_NUMBER_SUGGESTIONS = 10
CITATION_HELPER_THRESHOLD_FREQUENCY = 1
API_URL = 'https://api.adsabs.harvard.edu'
CITATION_HELPER_SOLRQUERY_URL = '%s/v1/search/query' % API_URL
# Config for logging
CITATION_HELPER_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s\t%(process)d '
                      '[%(asctime)s]:\t%(message)s',
            'datefmt': '%m/%d/%Y %H:%M:%S',
        }
    },
    'handlers': {
        'file': {
            'formatter': 'default',
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/tmp/citation_helper.log',
        },
        'console': {
            'formatter': 'default',
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
# Define the autodiscovery endpoint
DISCOVERER_PUBLISH_ENDPOINT = '/resources'
# Advertise its own route within DISCOVERER_PUBLISH_ENDPOINT
DISCOVERER_SELF_PUBLISH = False
