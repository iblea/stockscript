#!/usr/bin/env python3

import config
import webserver_run as webserver

config.exist_config()

flask_config = config.data.get("flask")

webserver.run_webserver_thread(
    http_port=flask_config.get("http_port", 0),
    https_port=flask_config.get("https_port", 0)
)

from time import sleep
while True:
    sleep(1)
