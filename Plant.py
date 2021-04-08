from db import DropletDB
import datetime

class Plant:
	def __init__(self, plant_id):
		plant_data = DropletDB.getPlant(plant_id)
		
		self.id = plant_data['id']
		self.name = plant_data['name']

		self.pump = {}
		self.pump['id'] = plant_data['pump_id']
		self.pump['pin'] = DropletDB.getPumpPin(self.pump['id'])
		self.pump['irrigations'] = DropletDB.getIrrigations(self.pump['id'])
		self.pump['getLog'] = self.getLogIrrigation
		
		self.humidity = {}
		self.humidity['sensor_id'] = plant_data['humidity_sensor_id']
		self.humidity['triggers'] = DropletDB.getTriggersBySensorId(self.humidity['sensor_id'])
		self.humidity['readings'] = DropletDB.getSensorReadings(self.humidity['sensor_id'])
		self.humidity['getLog'] = self.getLogHumidity

		self.light = {}
		self.light['sensor_id'] = plant_data['light_sensor_id']
		self.light['triggers'] = DropletDB.getTriggersBySensorId(self.light['sensor_id'])
		self.light['readings'] = DropletDB.getSensorReadings(self.light['sensor_id'])
		self.light['getLog'] = self.getLogLight
	
	def getLogIrrigation(self, format_timestamps = False, quantize_mins = False):
		logs = self.pump['irrigations']
		if quantize_mins is not False:
			logs = self.roundTimestampMinutes(logs, quantize_mins, 'timestamp')
		if format_timestamps:
			logs = self.formatTimestamps(logs, 'timestamp')
		return logs
	
	def getLogHumidity(self, format_timestamps = False, quantize_mins = False):
		logs = self.humidity['readings']
		if quantize_mins is not False:
			logs = self.roundTimestampMinutes(logs, quantize_mins, 'timestamp')
		if format_timestamps:
			logs = self.formatTimestamps(logs, 'timestamp')
		return logs
	
	def getLogLight(self, format_timestamps = False, quantize_mins = False):
		logs = self.light['readings']
		if quantize_mins is not False:
			logs = self.roundTimestampMinutes(logs, quantize_mins, 'timestamp')
		if format_timestamps:
			logs = self.formatTimestamps(logs, 'timestamp')
		return logs
	
	def getChartAll(self, quantize_mins = 30):
		in_format = '%Y-%m-%d %H:%M:%S'

		labels = []
		datasets = {'irrigation':[], 'humidity':[], 'light':[]}
		irrigations = sorted(self.getLogIrrigation(False, quantize_mins), key=lambda item: item['timestamp'])
		humidity = sorted(self.getLogHumidity(False, quantize_mins), key=lambda item: item['timestamp'])
		light = sorted(self.getLogLight(False, quantize_mins), key=lambda item: item['timestamp'])		

		earliest_timestamp = None
		if len(humidity):
			earliest_timestamp = datetime.datetime.strptime(humidity[0]['timestamp'], in_format)

		if len(light):
			earliest_light_timestamp = datetime.datetime.strptime(light[0]['timestamp'], in_format)
			if earliest_timestamp is None or earliest_timestamp > earliest_light_timestamp:
				earliest_timestamp = earliest_light_timestamp
		
		if earliest_timestamp is not None:
			now = datetime.datetime.now()
			timestamp_cursor = earliest_timestamp
			while timestamp_cursor < now:
				labels.append(timestamp_cursor.strftime(in_format))
				timestamp_cursor = timestamp_cursor + datetime.timedelta(minutes=quantize_mins)
		
		for ts in labels:
			irrigation_found = False
			for item in irrigations:
				if item['timestamp'] == ts:
					datasets['irrigation'].append(item['amount_ml'])
					irrigation_found = True

			if not irrigation_found:
				datasets['irrigation'].append(None)

			humidity_found = False
			for item in humidity:
				if item['timestamp'] == ts:
					datasets['humidity'].append(item['value'])
					humidity_found = True
			
			if not humidity_found:
				datasets['humidity'].append(None)

			light_found = False
			for item in light:
				if item['timestamp'] == ts:
					datasets['light'].append(item['value'])

			if not light_found:
				datasets['light'].append(None)
		
		labels = self.formatTimestamps(labels)
					
		return (labels,datasets)
	
	@classmethod
	def formatTimestamps(cls, data, key = None):
		in_format = '%Y-%m-%d %H:%M:%S'
		out_format = '%H:%M'
		long_out_format = '%d.%m. %H:%M'
		last_date = None
		if key is not None:
			for reading in data:
				timestamp = datetime.datetime.strptime(reading['timestamp'], in_format)
				if last_date is not None and last_date.date() == timestamp.date():
					reading['timestamp'] = timestamp.strftime(out_format)
				else:
					reading['timestamp'] = timestamp.strftime(long_out_format)
				last_date = timestamp
		else:
			for idx, entry in enumerate(data):
				timestamp = datetime.datetime.strptime(entry, in_format)
				if last_date is not None and last_date.date() == timestamp.date():
					data[idx] = timestamp.strftime(out_format)
				else:
					data[idx] = timestamp.strftime(long_out_format)
				last_date = timestamp
		return data
	
	@staticmethod
	def roundTimestampMinutes(data, target_mins, key = None):
		if 60 % target_mins != 0 or target_mins <= 0:
			return data

		in_format = '%Y-%m-%d %H:%M:%S'
		if key is not None:
			for entry in data:
				timestamp = datetime.datetime.strptime(entry[key], in_format)
				rounded_mins = round(timestamp.minute / target_mins) * target_mins
				timestamp = timestamp.replace(minute=rounded_mins % 60, second=0)
				if rounded_mins == 60:
					timestamp = timestamp + datetime.timedelta(hours=1)
				entry[key] = timestamp.strftime(in_format)
		else:
			for idx, entry in enumerate(data):
				timestamp = datetime.datetime.strptime(entry, in_format)
				rounded_mins = round(timestamp.minute / target_mins) * target_mins
				timestamp = timestamp.replace(minute=rounded_mins % 60, second=0)
				if rounded_mins == 60:
					timestamp = timestamp + datetime.timedelta(hours=1)
				data[idx] = timestamp.strftime(in_format)
		return data