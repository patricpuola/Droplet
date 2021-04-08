#!/usr/bin/python3
# Program: Droplet Irrigation system 0.1
# Author: Patric Puola
import sys
import conf
from db import DropletDB

flags = sys.argv

try:
	import RPi.GPIO as GPIO, sys, time, spidev
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
except RuntimeError:
	print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by using 'sudo' to run your script")
	sys.exit(1)

if "setup" in flags:
	DropletDB.initialize()

if "humidity" in flags:
	SPI_PORT = 0
	SPI_DEVICE = 0

	spi = spidev.SpiDev()
	spi.open(SPI_PORT, SPI_DEVICE)
	spi.max_speed_hz = 1350000

def mapValue(value, in_min = 0, in_max = 1024, out_min = 0, out_max = 100, precision = 2, invert=False):
	in_min = float(in_min)
	in_max = float(in_max)
	out_min = float(out_min)
	out_max = float(out_max)

	in_range = in_max-in_min
	out_range = out_max-out_min
	multiplier = out_range/in_range

	if invert is True:
		return round((out_max - ((value-in_min)*multiplier)+out_min),precision)
	else:
		return round(((value-in_min)*multiplier)+out_min,precision)


def analogInput(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

def collectHumidity():
	moisture_basil = mapValue(value=analogInput(conf.PIN_HUMIDITY_BASIL), precision=1, invert=True)
	DropletDB.addReading(conf.PLANT_BASIL, moisture_basil)
	moisture_peppermint = mapValue(value=analogInput(conf.PIN_HUMIDITY_PEPPERMINT), precision=1, invert=True)
	DropletDB.addReading(conf.PLANT_PEPPERMINT, moisture_peppermint)

if "humidity" in flags:
	collectHumidity()

if "dump" in flags:
	data = DropletDB.getAll()
	print(data)

if "define-sensor" in flags:
	sensor_id = flags[2]
	sensor_type = flags[3]
	sensor_name = flags[4]
	DropletDB.defineSensor(sensor_id, sensor_type, sensor_name)
	print(sensor_name+" added")