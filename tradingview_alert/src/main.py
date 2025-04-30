#!/usr/bin/env python3

import os
import sys
import json

SCRIPT_DIR: str = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE: str = "conf/config.json"
CONFIG_PATH: str = os.path.join(SCRIPT_DIR, CONFIG_FILE)

def exist_config() -> None:
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Configuration file '{CONFIG_PATH}' not found!")
        print(f"Please config_sample.json to {CONFIG_FILE} and run again.")
        print("command: ")
        print(f"cp conf/config_sample.json {CONFIG_FILE}")
        sys.exit(1)

exist_config()



