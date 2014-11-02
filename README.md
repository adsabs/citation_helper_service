Start with

	python api.py
  
and do a request from the command line like so

	curl -H "Content-Type: application/json" -X POST -d '{"bibcodes":[""1980ApJS...44..169S","1980ApJS...44..193S""]}' http://localhost:5000/suggestions

and you should get back results from the Citation Helper.
