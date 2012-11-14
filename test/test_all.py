#!/usr/bin/env python2

# Copyright (C) 2012 MetaBrainz Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import codecs
import unittest
from os.path import abspath, join, dirname
from contextlib import closing
from coverart_redirect_server import load_config
from coverart_redirect.server import Server
from werkzeug.wrappers import Response
from werkzeug.test import Client

_root = dirname (dirname (abspath (__file__)))

class All (unittest.TestCase):

    @classmethod
    def setUpClass (cls):
        config = load_config (test=True)
        app = Server (config)

        sqlfile = join (_root, "test", "cover_art_archive.sql")
        with codecs.open (sqlfile, "rb", "utf-8") as c:
            with closing(app.engine.connect()) as connection:
                connection.execute (c.read ())


    def setUp (self):
        config = load_config (test=True)
        app = Server (config)

        self.server = Client (app, Response)


    def verifyRedirect (self, src, dst):
        response = self.server.get (src)
        self.assertEqual (response.status, b'307 Temporary Redirect')
        self.assertEqual (response.headers['Location'], dst)
        self.assertEqual (response.data, b"See: %s\n" % (dst))


    def test_caa_index (self):

        response = self.server.get ('/')

        self.assertEqual (response.status, b'200 OK')
        self.assertEqual (response.mimetype, b'text/html')
        self.assertTrue (b'<title>Cover Art Archive</title>' in response.data)
        self.assertTrue (b'Images in the archive are curated' in response.data)


    def test_front (self):

        response = self.server.get ('/release/98f08de3-c91c-4180-a961-06c205e63669/front')
        self.assertEqual (response.status, b'404 Not Found')
        self.assertTrue (response.data.startswith (b'No front cover image found for'))

        expected = 'http://archive.org/download/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80-100000001'
        req = '/release/353710ec-1509-4df9-8ce2-9bd5011e3b80'

        self.verifyRedirect (req + '/front',         expected + '.jpg')
        self.verifyRedirect (req + '/front.jpg',     expected + '.jpg')
        self.verifyRedirect (req + '/front-250',     expected + '_thumb250.jpg')
        self.verifyRedirect (req + '/front-250.jpg', expected + '_thumb250.jpg')
        self.verifyRedirect (req + '/front-500',     expected + '_thumb500.jpg')
        self.verifyRedirect (req + '/front-500.jpg', expected + '_thumb500.jpg')


    def test_back (self):

        response = self.server.get ('/release/98f08de3-c91c-4180-a961-06c205e63669/back')
        self.assertEqual (response.status, b'404 Not Found')
        self.assertTrue (response.data.startswith (b'No back cover image found for'))

        expected = 'http://archive.org/download/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80-999999999'
        req = '/release/353710ec-1509-4df9-8ce2-9bd5011e3b80'

        self.verifyRedirect (req + '/back',         expected + '.jpg')
        self.verifyRedirect (req + '/back.jpg',     expected + '.jpg')
        self.verifyRedirect (req + '/back-250',     expected + '_thumb250.jpg')
        self.verifyRedirect (req + '/back-250.jpg', expected + '_thumb250.jpg')
        self.verifyRedirect (req + '/back-500',     expected + '_thumb500.jpg')
        self.verifyRedirect (req + '/back-500.jpg', expected + '_thumb500.jpg')


    def test_image (self):

        # response = self.server.get ('/release/353710ec-1509-4df9-8ce2-9bd5011e3b80/444444444.jpg')
        # self.assertEqual (response.status, b'404 Not Found')
        # self.assertTrue (response.data.startswith (b'image 444444444 not found for'))

        expected = 'http://archive.org/download/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80-999999999'
        req = '/release/353710ec-1509-4df9-8ce2-9bd5011e3b80/999999999'

        self.verifyRedirect (req + '.jpg',     expected + '.jpg')
        self.verifyRedirect (req + '-250.jpg', expected + '_thumb250.jpg')
        self.verifyRedirect (req + '-500.jpg', expected + '_thumb500.jpg')


    def test_release_index (self):

        # response = self.server.get ('/release/98f08de3-c91c-4180-a961-06c205e63669/')
        # self.assertEqual (response.status, b'404 Not Found')
        # self.assertTrue (response.data.startswith (b'No cover art found for'))

        expected = 'http://archive.org/download/mbid-353710ec-1509-4df9-8ce2-9bd5011e3b80'
        req = '/release/353710ec-1509-4df9-8ce2-9bd5011e3b80'

        self.verifyRedirect (req + '/', expected + '/index.json')