"""
The MIT License (MIT)

Copyright (c) 2023-present MrSniFo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from json import (load, decoder)


class Config(object):
    __slots__ = ('path', 'file')

    def __init__(self, path: str):
        self.path = path
        self.file = None

    def __enter__(self):
        while True:
            try:
                self.file = open(file=self.path, mode='r')
                return self
            except FileNotFoundError:
                self.file = open(file=self.path, mode='w')
                self.file.write(self.default)
                self.file.close()

    @property
    def config(self) -> dict | bool:
        """
        This function loads the configuration file.
        """
        try:
            _load = load(self.file)
            return _load
        except decoder.JSONDecodeError:
            return False

    @property
    def default(self) -> str:
        """
        This function returns the default configuration file.
        """
        config = """{
  "loop": true,
  "threads": 10,

  "client_id": "kimne78kx3ncx6brgo4mv6wki5h1ko",

  "stream": {
    "max_uptime": 3600,
    "viewers": {
      "enable": false,
      "min": 0,
      "max": 100
    }
  },

  "keywords": [
    "Love",
    "Cake",
    "Giveaway",
    "MrSnifo"
  ],

  "category-only":{
    "enable": false,
    "categories": [
      "Just Chatting",
      "I'm Only Sleeping",
      "Pools, Hot Tubs, and Beaches",
      "ASMR",
      "talk shows & podcasts",
      "Sports"
    ],
    "no-category": true
  },

  "block": {
    "enable": false,
    "usernames": ["Nightbot", "StreamElements", "Streamlabs", "SoundAlerts",
     "PokemonCommunityGame", "RestreamBot", "PretzelRocks", "Wizebot"]
    }

}"""
        return config

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
