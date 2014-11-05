SECRET_KEY = 'this should be changed'
MAX_HITS = 10000    
MAX_INPUT = 500
MAX_SUBMITTED = 1000
CHUNK_SIZE = 100
NUMBER_SUGGESTIONS = 10
SQLALCHEMY_DATABASE_URI = ''
THRESHOLD_FREQUENCY = 1
SOLRQUERY_URL = 'http://adswhy:9000/solr/collection1/select'
#This section configures this application to act as a client, for example to query solr via adsws
CLIENT = {
  'TOKEN': 'we will provide an api key token for this application'
}
