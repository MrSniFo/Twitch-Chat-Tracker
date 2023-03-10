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

from datetime import datetime, timedelta
from collections.abc import Generator


class Streams(object):
    """
    Retrieving the latest twitch streams.
    """
    __slots__ = ('headers', 'season')

    def __init__(self, client_id: str):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/110.0.0.0 Safari/537.36",
            "Client-Id": client_id,
        }
        self.season = session()

    def latest(self, seconds: int) -> Generator[dict]:
        """
        This function returns the latest twitch streams.

        :param seconds:`int`
            max stream time

        :return:`iter[dict]`
        """

        payload = '[{"operationName":"BrowsePage_Popular","variables":{"imageWidth":50,"limit":30,' \
                  '"platformType":"all","options":{"sort":"RECENT","freeformTags":null,"tags":[],' \
                  '"recommendationsContext":{"platform":"web"},"requestID":"JIRA-VXP-2397"},' \
                  '"sortTypeIsRecency":true},"extensions":{"persistedQuery":{"version":1,' \
                  '"sha256Hash":"b32fa28ffd43e370b42de7d9e6e3b8a7ca310035fdbb83932150443d6b693e4d"}}}]'
        # Request error retry.
        _retry: int = 0
        # Seconds
        max_duration: int = 0
        while max_duration <= seconds:
            try:
                request = self.season.post(url="https://gql.twitch.tv/gql", headers=self.headers, data=payload)
                if request.status_code == 200:
                    _retry = 0
                    # keeps trucking the chunks.
                    cursor = None
                    streams = request.json()[0]['data']['streams']
                    if streams is not None and len(streams) != 0:
                        for stream in streams['edges']:
                            cursor = stream['cursor']
                            created_at = stream['node']['createdAt']
                            stream = stream['node']
                            duration = None
                            if stream['broadcaster'] is not None:
                                # Seconds.
                                if created_at is not None:
                                    duration = (datetime.utcnow() - datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ"))
                                    if duration.seconds > max_duration:
                                        max_duration = duration.seconds
                                    duration = str(timedelta(seconds=duration.seconds))

                                yield {'username': stream['broadcaster']['login'],
                                       'category': stream['game'],
                                       'viewers': stream['viewersCount'],
                                       'duration': duration}

                        # Uploading the payload with the latest cursor.
                        payload = '[{"operationName":"BrowsePage_Popular","variables":{"imageWidth":50,"limit":30,' \
                                  '"platformType":"all","options":{"sort":"RECENT","freeformTags":null,"tags":[],' \
                                  '"recommendationsContext":{"platform":"web"},"requestID":"JIRA-VXP-2397"},' \
                                  '"sortTypeIsRecency":true,' \
                                  '"cursor":"%s"},' \
                                  '"extensions":{"persistedQuery":{"version":1,' \
                                  '"sha256Hash":' \
                                  '"b32fa28ffd43e370b42de7d9e6e3b8a7ca310035fdbb83932150443d6b693e4d"}}}]' % cursor
                    else:
                        break
                else:
                    if _retry == 3:
                        break
                    else:
                        _retry += 1
            except ConnectTimeout:
                if _retry == 3:
                    break
                else:
                    _retry += 1
