[![Build Status](https://travis-ci.org/adsabs/citation_helper_service.svg?branch=master)](https://travis-ci.org/adsabs/citation_helper_service)
Start with

	python wsgi.py
  
and do a request from the command line like so

	curl -H "Content-Type: application/json" -X POST -d '{"bibcodes":["1980ApJS...44..169S","1980ApJS...44..193S"]}' http://localhost:4000

and you should get back results from the Citation Helper.
