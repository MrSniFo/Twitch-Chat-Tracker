"""
The MIT License (MIT)

Copyright (c) 2022-present MrSniFo

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

# ------ Core ------
from .models import Streams, Chat, Config, logger
# ------ Threading & Queue ------
from queue import Queue
from threading import Thread


class Bot:
    __slots__ = ("config", "logger", "counter", "queue")

    def __init__(self):
        # logging event.
        self.logger = logger()
        # Loading config.
        with Config(path="config.json") as file:
            self.config = file.config

        # Counters
        self.counter = {"checks": 0, "checked-stream": 0}

        if self.config:
            # Threading & Queue.
            self.queue = Queue()
            for thread_number in range(self.config["threads"]):
                worker = Thread(target=self.checking, args=(self.queue, thread_number,), daemon=True)
                worker.start()

    def start(self):
        self.logger.info("Launching the Twitch chat tracker.")
        # Ensure that there is no config errors.
        if self.config:
            while self.config["loop"]:
                self.logger.info(f"[{self.counter['checks'] + 1}] Searching for streams to monitor...")
                max_uptime = self.config["stream"]["max_uptime"]
                streams = Streams(client_id=self.config["client_id"]).latest(seconds=max_uptime)
                self.logger.info("Starting chat log extraction process\n")
                # Maximum and minimum stream viewers.
                _min: int = self.config["stream"]["viewers"]["min"]
                _max: int = self.config["stream"]["viewers"]["max"]
                for stream in streams:
                    if (not self.config["stream"]["viewers"]["enable"]) or (_max >= stream["viewers"] >= _min):
                        # Stream category.
                        _s_c: dict | None = stream["category"]
                        # Categories.
                        _cs: list = list(map(str.lower, self.config["category-only"]["categories"]))
                        # No Category.
                        _n_c: bool = self.config["category-only"]["no-category"]
                        if (not self.config["stream"]["viewers"]["enable"]) or (_s_c is None and _n_c) or \
                                (_s_c is not None and _s_c["name"].lower() in _cs):
                            self.counter['checked-stream'] += 1
                            self.queue.put(item=stream)
                if not self.config["loop"]:
                    # Blocks until all items in the Queue have been gotten and processed.
                    self.queue.join()
                self.counter['checks'] += 1
                self.logger.info(f"Finished with a total checked streams: {self.counter['checked-stream'] + 1}.")
                self.counter['checked-stream'] = 0
        else:
            self.logger.error("The configuration file is corrupt, you can delete it to create a new one.")

    def checking(self, queue, thread):
        while True:
            stream = queue.get()
            chat = Chat(client_id=self.config["client_id"], username=stream["username"])
            _last_channel: str | None = None
            for user in chat.history():
                _b_us = list(map(str.lower, self.config["block"]["usernames"]))
                if (not self.config["block"]["enable"]) or user["username"].lower() not in _b_us:
                    keywords_found: list = chat.find_keywords(text=user["message"], keywords=self.config["keywords"])
                    if len(keywords_found) >= 1:
                        if _last_channel != stream["username"]:
                            self.logger.warning(
                                f"[T{thread + 1}] [{stream['duration']}]"
                                f" {'https://www.twitch.tv/' + stream['username']}")
                            _last_channel = stream["username"]
                        self.logger.warning(f"{user['role']}{user['username']}: {user['message']}")
                        self.logger.warning(f"Keyword(s): {', '.join(keywords_found)}\n")
            queue.task_done()
