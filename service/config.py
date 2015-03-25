SECRET_KEY = 'this should be changed'
MAX_HITS = 10000    
MAX_INPUT = 500
MAX_SUBMITTED = 100
CHUNK_SIZE = 100
NUMBER_SUGGESTIONS = 10
THRESHOLD_FREQUENCY = 1
SOLRQUERY_URL = 'http://localhost:9000/solr/collection1/select'
#This section configures this application to act as a client, for example to query solr via adsws
CLIENT = {
  'TOKEN': 'we will provide an api key token for this application'
}
# Define the autodiscovery endpoint
DISCOVERER_PUBLISH_ENDPOINT = '/resources'
# Advertise its own route within DISCOVERER_PUBLISH_ENDPOINT
DISCOVERER_SELF_PUBLISH = False
