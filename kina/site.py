#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

import flask

from simplejson import dumps

from scraper import Scraper

app = flask.Flask('kina')
scraper = Scraper()

def json_response(data, status=200):
    content_type = 'application/json; charset=utf-8'
    return flask.Response(data, status=status, content_type=content_type)

@app.route('/town/')
def town():
    return json_response(dumps(scraper.towns))

@app.route('/town/<int:town>/cinema/')
def cinema(town):
    return json_response(dumps(scraper.cinemas(town)))

@app.route('/town/<int:town>/cinema/<int:cinema>/movie/')
def cinema_movie(town, cinema):
    return json_response(dumps(scraper.movies(town, cinema)))

@app.route('/town/<int:town>/movie/')
def movie(town):
    return json_response(dumps(scraper.movies(town)))

@app.route('/town/<int:town>/movie/<int:movie>/cinema/')
def movie_cinema(town, movie):
    return json_response(dumps(scraper.cinemas(town, movie)))

if __name__ == '__main__':
    app.debug = True
    app.run()

# vim:set sw=4 ts=4 et:
