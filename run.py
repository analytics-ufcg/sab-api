#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask
from login import app
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true')

if __name__ == '__main__':
	app.debug = parser.parse_args().debug
	app.run(host='0.0.0.0', port=5003, threaded=True, use_reloader=True)
