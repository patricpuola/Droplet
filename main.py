#!/usr/bin/python3
# Program: Droplet Irrigation system 0.1
# Author: Patric Puola

import conf
import sqlite3
import flask
import datetime
from db import DropletDB

app = flask.Flask(__name__)

@app.route('/')
def monitor():
	sensor_data = DropletDB.getAll()
	in_format = '%Y-%m-%d %H:%M:%S'
	out_format = '%H:%M'
	for sensor in sensor_data:
		for reading in sensor['data']:
			mysql_timestamp = datetime.datetime.strptime(reading['timestamp'], in_format)
			reading['timestamp_formatted'] = mysql_timestamp.strftime(out_format)
	return flask.render_template('index.html', sensor_data=sensor_data)

if __name__ == '__main__':
	app.debug = True
	app.run(host="10.10.10.100", port=80)
