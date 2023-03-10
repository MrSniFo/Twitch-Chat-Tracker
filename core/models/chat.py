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

from requests import session
from requests.exceptions import ConnectTimeout

from re import compile, escape, IGNORECASE
from collections.abc import Generator

from time import sleep


class Chat(object):
    """
    Retrieving Chat History of a twitch channel.
    """
    __slots__ = ('headers', 'username', 'season')

    def __init__(self, client_id: str, username: str):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/110.0.0.0 Safari/537.36",
            "Client-Id": client_id,
        }
        self.username = username
        self.season = session()

    def history(self) -> Generator[dict]:
        """
        This function returns the latest messages.

        :return:`iter[dict]`
        """

        payload = '[{"operationName":"MessageBufferChatHistory","variables":{"channelLogin":"%s"},"extensions":{' \
                  '"persistedQuery":{"version":1,' \
                  '"sha256Hash":"432ef3ec504a750d797297630052ec7c775f571f6634fdbda255af9ad84325ae"}}}]' % self.username
        try:
            request = self.season.post(url="https://gql.twitch.tv/gql", headers=self.headers, data=payload)
            if request.status_code == 200:
                # Sometimes twitch returns error.
                if len(request.json()) == 1:
                    messages = request.json()[0]['data']['channel']
                    if messages is not None:
                        for msg in messages['recentChatMessages']:
                            if msg.get("sender") is not None:
                                _role = ""
                                if len(msg.get("senderBadges")) != 0:
                                    _role = f"[{msg['senderBadges'][0]['setID']}] "
                                yield {'username': msg['sender']['login'],
                                       'message': msg['content']['text'],
                                       'role': _role}
        except ConnectTimeout:
            sleep(1.5)

    @staticmethod
    def find_keywords(text: str, keywords: list) -> list:
        found_keywords = []
        compiled_patterns = {word: compile(r"\b{}\b".format(escape(word)), IGNORECASE) for word in keywords}
        for pattern in compiled_patterns.values():
            matches = pattern.findall(text)
            found_keywords.extend(matches)
        return found_keywords
