#!/usr/bin/python -tt
# -*- coding: utf-8 -*-

from time import time
from functools import wraps
from collections import OrderedDict
from urllib import urlencode, urlopen

import html5lib as html5
import re

def cached(seconds):
    def decorate(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_cache'):
                self._cache = {}

            key = (fn,) + tuple(args) + tuple(sorted(kwargs.items()))

            if key not in self._cache or self._cache[key][0] < time():
                result = fn(self, *args, **kwargs)
                self._cache[key] = (time() + seconds, result)

            return self._cache[key][1]

        return wrapper
    return decorate

class Scraper(object):
    base_url = 'http://m.dokina.tiscali.cz/ajax/program?'
    praha = 554782

    def request(self, **options):
        """
        Perform a remote theater program request and return the html5
        document with results.  You need to extract details yourself.
        """

        fp = urlopen(self.base_url + urlencode(options))
        data = '<div>' + fp.read() + '</div>'
        fp.close()

        return html5.parseFragment(data, 'div', 'lxml', 'utf-8', False).pop()

    @property
    @cached(3600)
    def towns(self):
        """
        Return mapping of town names to their identifiers.
        """

        towns = OrderedDict([('Praha', self.praha)])
        data = self.request(tab='movies')

        opts = data.xpath('//select[@class="choice-town"]//option[@value]')
        for opt in opts:
            m = re.search('.*townId=([0-9]*)', opt.attrib['value'])
            towns[opt.text] = int(m.group(1))

        return towns

    @cached(300)
    def cinemas(self, town=praha, movie=None):
        """
        Iterate over cinemas showing specified movie in the specified town.
        """

        if movie:
            data = self.request(tab='cinemas', townId=town, fixedMovie=1, movieId=movie)
        else:
            data = self.request(tab='cinemas', townId=town)

        cinemas =  []

        for a in data.xpath('//ul[2]//h3/..'):
            name = a.xpath('h3')[0].text.strip()
            data_id = int(re.sub('.*-', '', a.xpath('@href')[0]))
            times = a.xpath('p[@class="times"]/strong/text()')

            cinemas.append({
                'id': data_id,
                'name': name,
                'times': [t.replace('.', ':') for t in times],
            })

        return cinemas

    @cached(300)
    def movies(self, town=praha, cinema=None):
        """
        Iterate over movies in the specified cinema or town.
        """

        if cinema:
            data = self.request(tab='movies', townId=town, fixedCinema=1, cinemaId=cinema)
        else:
            data = self.request(tab='movies', townId=town)

        movies = []

        for a in data.xpath('//ul[2]//h3/..'):
            name = a.xpath('h3')[0].text.strip()
            data_id = int(re.sub('.*-', '', a.xpath('@href')[0]))
            times = a.xpath('p[@class="times"]/strong/text()')
            imdb = a.xpath('p[@class="imdb"]/strong/text()') + ['unknown']
            img = a.xpath('.//img/@src')[0]

            movies.append({
                'id': data_id,
                'name': name,
                'times': [t.replace('.', ':') for t in times],
                'rating': imdb[0],
                'img': img,
            })

        return movies


# vim:set sw=4 ts=4 et:
