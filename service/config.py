# Maximum number of rows to be returned from Solr
CITATION_HELPER_MAX_HITS = 10000
# Maximum number of bibcodes in input (excess will be ignored)
CITATION_HELPER_MAX_INPUT = 500
# Maximum number allowed in submitted bibcodes
CITATION_HELPER_MAX_SUBMITTED = 100
# Bibcode input list will be split into chunks of this size
CITATION_HELPER_CHUNK_SIZE = 100
# The maximum number of suggestions returned by the service
CITATION_HELPER_NUMBER_SUGGESTIONS = 10
# Minimal score for papers to be included in results
CITATION_HELPER_THRESHOLD_FREQUENCY = 1
# Where to query Solr
CITATION_HELPER_SOLR_PATH = 'https://api.adsabs.harvard.edu/v1/search/query'
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
            'filename': '/tmp/citation_helper_app.log',
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
