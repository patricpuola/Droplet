#!/usr/bin/python3
import conf
import sqlite3
import datetime

class DropletDB:
	DATABASE_FILE = conf.ROOT.parent / 'droplet.db'
	connection = None

	@classmethod
	def get(cls):
		if cls.connection is not None:
			cls.connection = None
		cls.connection = sqlite3.connect(str(cls.DATABASE_FILE))
		return cls.connection

	@staticmethod
	def initialize():
		con = DropletDB.get()
		cur = con.cursor()
		
		cur.execute('''CREATE TABLE IF NOT EXISTS sensors (id INTEGER PRIMARY KEY, type INT, name VARCHAR(50), pin INT)''')
		cur.execute('''CREATE TABLE IF NOT EXISTS pumps (id INTEGER_PRIMARY_KEY, pin INT)''')
		cur.execute('''CREATE TABLE IF NOT EXISTS plants (id INTEGER PRIMARY KEY, name VARCHAR(50), pump_id INT, humidity_sensor_id INT, light_sensor_id)''')
		cur.execute('''CREATE TABLE IF NOT EXISTS readings (id INTEGER PRIMARY KEY, sensor_id INT, value FLOAT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
		cur.execute('''CREATE TABLE IF NOT EXISTS irrigations (id INTEGER PRIMARY KEY, pump_id INT, amount_ml INT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
		cur.execute('''CREATE TABLE IF NOT EXISTS triggers (id INTEGER PRIMARY KEY, pump_id INT, amount_ml INT, sensor_id INT, threshold FLOAT, wait_period_mins INT)''')
		con.commit()

		for plant in conf.INIT_DB['plants']:
			cur.execute('''INSERT INTO plants (id, name, pump_id, humidity_sensor_id, light_sensor_id) VALUES (?,?,?,?,?)''', plant)
		for sensor in conf.INIT_DB['sensors']:
			cur.execute('''INSERT INTO sensors (id, type, name) VALUES (?,?,?)''', sensor)
		for pump in conf.INIT_DB['pumps']:
			cur.execute('''INSERT INTO pumps (id) VALUES (?)''', pump)
		con.commit()

	@staticmethod
	def addReading(sensor_id, value):
		con = DropletDB.get()
		cur = con.cursor()
		data_insert = (sensor_id, value)
		cur.execute("INSERT INTO readings (sensor_id, value) VALUES (?, ?)", data_insert)
		con.commit()

	@staticmethod
	def getAll(limit = 50):
		con = DropletDB.get()
		cur = con.cursor()
		plants = []
		cur.execute("SELECT id, name, pump_id, humidity_sensor_id, light_sensor_id FROM plants")
		plant_rows = cur.fetchall()

		for plant in plant_rows:
			plants.append({'id':plant[0], 'name':plant[1], 'pump_id':plant[2], 'humidity':{'sensor_id':plant[3], 'sensor_pin':None, 'data':[]}, 'light':{'sensor_id':plant[4], 'sensor_pin':None, 'data':[]}})

		for plant in plants:
			params = (plant['humidity']['sensor_id'], limit)
			cur.execute("SELECT value, datetime(timestamp, 'localtime') as timestamp FROM readings WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT ?", params)
			humidity_rows = cur.fetchall()
			for row in humidity_rows:
				plant['humidity']['data'].append({'value':row[0], 'timestamp': row[1]})
		return plants

	@staticmethod
	def getActivatedTriggers():
		con = DropletDB.get()
		cur = con.cursor()
		triggers = []
		active_triggers = []
		cur.execute("SELECT id, pump_id, amount_ml, sensor_id, threshold, wait_period_mins from triggers")
		trigger_rows = cur.fetchall()
		for trigger in trigger_rows:
			triggers.append({'id':trigger[0], 'pump_id':trigger[1], 'amount_ml':trigger[2], 'sensor_id':trigger[3], 'threshold':trigger[4], 'wait_period_mins':trigger[5]})
		
		for trigger in triggers:
			date_limit = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=trigger['wait_period_mins'])
			params = (trigger['pump_id'], date_limit.strftime("%Y-%m-%d H:M:S"))
			cur.execute("SELECT 1 FROM irrigations WHERE pump_id = ? AND timestamp > ? LIMIT 1", params)
			irrigations = cur.fetchall()
			if len(irrigations) > 0:
				continue
			
			params = (trigger['sensor_id'],)
			cur.execute("SELECT value FROM readings WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT 1", params)
			readings = cur.fetchall()
			if (readings[0][0] < trigger['threshold']):
				active_triggers.append(trigger)

		return active_triggers
	
	@staticmethod
	def getTriggersBySensorId(sensor_id):
		triggers = []
		if sensor_id is None:
			return triggers
		con = DropletDB.get()
		cur = con.cursor()
		sensor = (sensor_id,)
		cur.execute("SELECT id, amount_ml, threshold, wait_period_mins from triggers WHERE sensor_id = ?", sensor)
		trigger_rows = cur.fetchall()
		for trigger in trigger_rows:
			triggers.append({'id':trigger[0], 'amount_ml':trigger[1], 'threshold':trigger[2], 'wait_period_mins':trigger[3]})
		return triggers

	@staticmethod
	def getPumpPin(pump_id):
		con = DropletDB.get()
		cur = con.cursor()
		params = (pump_id,)
		cur.execute("SELECT pin FROM pumps WHERE id = ?", params)
		pin = cur.fetchall()[0][0]
		return pin

	@staticmethod
	def truncate():
		con = DropletDB.get()
		cur = con.cursor()
		cur.execute("TRUNCATE TABLE IF EXISTS readings")
		con.commit()

	@staticmethod
	def defineSensor(id, type, name):
		con = DropletDB.get()
		cur = con.cursor()
		data_insert = (id, type, name)
		cur.execute("INSERT INTO sensors (id, type, name) VALUES (?, ?, ?)", data_insert)
		con.commit()
	
	@staticmethod
	def logIrrigation(pump_id, amount_ml):
		con = DropletDB.get()
		cur = con.cursor()
		data_insert = (pump_id, amount_ml)
		cur.execute("INSERT INTO irrigations (pump_id, amount_ml) VALUES (?, ?)", data_insert)
		con.commit()
	
	@staticmethod
	def getPlant(plant_id):
		con = DropletDB.get()
		cur = con.cursor()
		plant = (plant_id,)
		cur.execute("SELECT * FROM plants WHERE id = ? LIMIT 1", plant)
		(id, name, pump_id, humidity_sensor_id, light_sensor_id) = cur.fetchall()[0]
		return {'id':id, 'name':name, 'pump_id':pump_id, 'humidity_sensor_id':humidity_sensor_id, 'light_sensor_id':light_sensor_id}
	
	@staticmethod
	def getIrrigations(pump_id):
		irrigations = []
		if pump_id is None:
			return irrigations
		con = DropletDB.get()
		cur = con.cursor()
		pump = (pump_id,)
		cur.execute("SELECT amount_ml, datetime(timestamp, 'localtime') FROM irrigations WHERE pump_id = ?", pump)
		irrigation_rows = cur.fetchall()
		for i_row in irrigation_rows:
			irrigations.append({'amount_ml':i_row[0], 'timestamp':i_row[1]})
		return irrigations

	@staticmethod
	def getSensorReadings(sensor_id, limit = 50):
		readings = []
		if sensor_id is None:
			return readings
		con = DropletDB.get()
		cur = con.cursor()

		params = (sensor_id, limit)
		cur.execute("SELECT value, datetime(timestamp, 'localtime') as timestamp FROM readings WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT ?", params)
		reading_rows = cur.fetchall()
		for row in reading_rows:
			readings.append({'value':row[0], 'timestamp': row[1]})
		return readings

	@staticmethod
	def getPlantIds():
		plant_ids = []
		con = DropletDB.get()
		cur = con.cursor()
		cur.execute("SELECT id FROM plants")
		plant_rows = cur.fetchall()
		for row in plant_rows:
			plant_ids.append(row[0])
		return plant_ids