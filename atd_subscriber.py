#!/usr/bin/env python

import logging
import os
import sys
import time
import json
import threading
import importlib

from dxlclient.callbacks import EventCallback
from dxlclient.client import DxlClient
from dxlclient.client_config import DxlClientConfig
from dxlclient.message import Event, Request

# Configure local logger
logging.getLogger().setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

CONFIG_FILE = "/path/to/config/file"
config = DxlClientConfig.create_dxl_config_from_file(CONFIG_FILE)

# Import web.py module
web = importlib.import_module("web")

# Create the client
with DxlClient(config) as client:

    # Connect to the fabric
    client.connect()

    # Create and add event listener
    class MyEventCallback(EventCallback):
        def on_event(self, event):
            try:
                query = event.payload.decode()
                logger.info("Event received: " + query)
                
                query = query[:-3]
                query = json.loads(query)
                
                # Create Subscribed List for Web Gateway
                try:
                   for ips in query['Summary']['Ips']:
                      ipv4 = ips['Ipv4']
                      if not ipv4: pass
                      else: web.action(ipv4)
                except: pass
                
            except Exception as e:
                print e

        @staticmethod
        def worker_thread(req):
            client.sync_request(req)

    # Register the callback with the client
    client.add_event_callback('#', MyEventCallback(), subscribe_to_topic=False)
    client.subscribe("/mcafee/event/atd/file/report")

    # Wait forever
    while True:
        time.sleep(60)

