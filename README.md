[![Waffle.io - Columns and their card count](https://badge.waffle.io/adsabs/citation_helper_service.svg?columns=all)](https://waffle.io/adsabs/citation_helper_service)
[![Build Status](https://travis-ci.org/adsabs/citation_helper_service.svg?branch=master)](https://travis-ci.org/adsabs/citation_helper_service)
[![Coverage Status](https://coveralls.io/repos/adsabs/citation_helper_service/badge.svg)](https://coveralls.io/r/adsabs/citation_helper_service)
[![Code Climate](https://codeclimate.com/github/adsabs/citation_helper_service/badges/gpa.svg)](https://codeclimate.com/github/adsabs/citation_helper_service)
[![Issue Count](https://codeclimate.com/github/adsabs/citation_helper_service/badges/issue_count.svg)](https://codeclimate.com/github/adsabs/citation_helper_service)

Start with

	python wsgi.py
  
and do a request from the command line like so

	curl -H "Content-Type: application/json" -X POST -d '{"bibcodes":["1980ApJS...44..169S","1980ApJS...44..193S"]}' http://localhost:4000

and you should get back results from the Citation Helper.
