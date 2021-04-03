#!/usr/bin/python3
import conf
import sqlite3

class DropletDB:
	DATABASE_FILE = conf.ROOT.parent / 'droplet.db'
	connection = None

	@classmethod
	def get(cls):
		if cls.connection is None:
			cls.connection = sqlite3.connect(str(cls.DATABASE_FILE))
		return cls.connection

	@staticmethod
	def initialize():
		con = DropletDB.get()
		cur = con.cursor()
		cur.execute('''CREATE TABLE IF NOT EXISTS humidity (id INTEGER PRIMARY KEY, sensor_id INT, value FLOAT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
		cur.execute('''CREATE TABLE IF NOT EXISTS sensors (id INTEGER PRIMARY KEY, type INT, name VARCHAR(50))''')
		con.commit()

	@staticmethod
	def add(sensor_id, value):
		con = DropletDB.get()
		cur = con.cursor()
		data_insert = (sensor_id, value)
		cur.execute("INSERT INTO humidity (sensor_id, value) VALUES (?, ?)", data_insert)
		con.commit()

	@staticmethod
	def getAll(type = None, limit = 50):
		con = DropletDB.get()
		cur = con.cursor()
		sensors = []
		
		if type is not None:
			type_filter = (type,)
			cur.execute("SELECT id, type, name FROM sensors WHERE type = ?", type_filter)
		else:
			cur.execute("SELECT id, type, name FROM sensors")
		
		sensor_rows = cur.fetchall()
		for row in sensor_rows:
			sensors.append({'id':row[0], 'type':row[1], 'name':row[2], 'data':[]})

		for sensor in sensors:
			params = (sensor['id'], limit)
			cur.execute("SELECT value, datetime(timestamp, 'localtime') as timestamp FROM humidity WHERE sensor_id = ? ORDER BY timestamp DESC LIMIT ?", params)
			humidity_rows = cur.fetchall()
			for row in humidity_rows:
				sensor['data'].append({'value':row[0], 'timestamp': row[1]})
		return sensors

	@staticmethod
	def truncate():
		con = DropletDB.get()
		cur = con.cursor()
		cur.execute("TRUNCATE TABLE IF EXISTS humidity")
		con.commit()

	@staticmethod
	def defineSensor(id, type, name):
		con = DropletDB.get()
		cur = con.cursor()
		data_insert = (id, type, name)
		cur.execute("INSERT INTO sensors (id, type, name) VALUES (?, ?, ?)", data_insert)
		con.commit()
