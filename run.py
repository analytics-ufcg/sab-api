#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from flask import Flask
from resources import app 

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5003, threaded=True)