#!/usr/bin/python3
# Program: Droplet Irrigation system 0.1
# Author: Patric Puola

import conf
import sqlite3
import flask
import datetime
from db import DropletDB
import Plant

app = flask.Flask(__name__)

@app.route('/')
def monitor():
	plantdata = DropletDB.getAll()
	in_format = '%Y-%m-%d %H:%M:%S'
	out_format = '%H:%M'
	for plant in plantdata:
		for reading in plant['humidity']['data']:
			mysql_timestamp = datetime.datetime.strptime(reading['timestamp'], in_format)
			reading['timestamp_formatted'] = mysql_timestamp.strftime(out_format)
	plant_ids = DropletDB.getPlantIds()
	plants = []
	for pid in plant_ids:
		plant = Plant.Plant(pid)
		plant.chart_data = plant.getChartAll()
		plants.append(plant)
	return flask.render_template('index.html', plantdata=plantdata, plants=plants)

@app.route('/admin/trigger', methods=['GET','POST'])
def triggerUpdate():
	result = {'success':False, 'data':""}
	data = flask.request.get_json()
	if DropletDB.updateTrigger(data['trigger_id'], data['threshold'], data['amount_ml'], data['wait_period_mins']) is True:
		result['success'] = True
		result['data'] = 'OK'
	return result

if __name__ == '__main__':
	app.debug = True
	app.run(host="10.10.10.100", port=80)
