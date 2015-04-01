CITATION_HELPER_SECRET_KEY = 'this should be changed'
CITATION_HELPER_MAX_HITS = 10000    
CITATION_HELPER_MAX_INPUT = 500
CITATION_HELPER_MAX_SUBMITTED = 100
CITATION_HELPER_CHUNK_SIZE = 100
CITATION_HELPER_NUMBER_SUGGESTIONS = 10
CITATION_HELPER_THRESHOLD_FREQUENCY = 1
CITATION_HELPER_SOLRQUERY_URL = 'https://api.adsabs.harvard.edu/v1/search/query'
#This section configures this application to act as a client, for example to query solr via adsws
CITATION_HELPER_API_TOKEN = 'we will provide an api key token for this application'
# Define the autodiscovery endpoint
DISCOVERER_PUBLISH_ENDPOINT = '/resources'
# Advertise its own route within DISCOVERER_PUBLISH_ENDPOINT
DISCOVERER_SELF_PUBLISH = False
