#!/usr/bin/python3

# Program: Droplet Irrigation system 0.1
# Author: Patric Puola

import sys

flags = sys.argv

if len(flags) != 3:
	print("Invalid number of arguments")
	sys.exit(1)

MAX_AMOUNT = 30
AVAILABLE_PINS = [12,16,20,21]

pin = int(flags[1])
amount_ml = int(flags[2])

if pin not in AVAILABLE_PINS:
	print("Invalid pin")
	sys.exit(1)

if amount_ml > MAX_AMOUNT:
	print("Maximum amount exceeded, choose a smaller amount")
	sys.exit(1)

try:
	import RPi.GPIO as GPIO, sys, time, spidev
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
except RuntimeError:
	print("Error importing RPi.GPIO! This is probably because you need superuser privileges. You can achieve this by using 'sudo' to run your script")
	sys.exit(1)

GPIO.setup(12, GPIO.OUT)
GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

def milliliters_to_seconds(ml):
	#TODO
	return ml

def main():
		GPIO.output(pin, True)
		time.sleep(milliliters_to_seconds(amount_ml))
		GPIO.output(12, False)
		GPIO.cleanup()

try:
	main()
	print("OK")
except KeyboardInterrupt:
	GPIO.cleanup()
	print("Droplet stopped")
	sys.exit(0)
