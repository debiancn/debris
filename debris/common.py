#!/usr/bin/env python3
#
# debris.common -- common things for debris autobuild system
pass

import configparser

def load_config(filepath: str) -> configparser.ConfigParser:
    """
    load configuration file using configparser.

    return a ConfigParser instance.
    """
    config = configparser.ConfigParser()
    try:
        config.read(filepath)
    except:
        raise
# TODO: exception handler
    return config
