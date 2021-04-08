#!/usr/bin/python3

# Program: Droplet Irrigation system 0.1
# Author: Patric Puola

# WARNING! Reverse operation logic, motors connected to normally closed relays in a way that they don't run when mains power is connected to system
# GPIO.output(pin, False) = Flow
# GPIO.output(pin, True) = No flow

import sys

FLOWRATE_ML_PER_S = 1.731
FLOWRATE_S_PER_ML = 1/FLOWRATE_ML_PER_S
MAX_AMOUNT = 300
AVAILABLE_PINS = [12,16,20,21]

flags = sys.argv

if len(flags) != 3:
	print("Invalid number of arguments")
	print("Usage "+flags[0]+" raspi_pin amount_ml")
	print("Example: "+flags[0]+" "+str(AVAILABLE_PINS[0])+" 20")
	sys.exit(1)

pin = int(flags[1])
amount_ml = int(flags[2])

if pin not in AVAILABLE_PINS:
	print("ERROR: Invalid pin")
	sys.exit(1)

if amount_ml > MAX_AMOUNT:
	print("ERROR: Maximum amount exceeded, choose a smaller amount")
	sys.exit(1)

try:
	import RPi.GPIO as GPIO, sys, time, spidev
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
except RuntimeError:
	print("ERROR: Importing RPi.GPIO. This is probably because you need superuser privileges. You can achieve this by using 'sudo' to run your script")
	sys.exit(1)

for av_pin in AVAILABLE_PINS:
	GPIO.setup(av_pin, GPIO.OUT)
	GPIO.output(av_pin, True)

def milliliters_to_seconds(ml):
	return round(ml*FLOWRATE_S_PER_ML,1)

def main():
		GPIO.output(pin, False)
		time.sleep(milliliters_to_seconds(amount_ml))
		GPIO.output(pin, True)

try:
	main()
	GPIO.cleanup()
	print("OK")
	sys.exit(0)
except KeyboardInterrupt:
	GPIO.cleanup()
	print("Droplet stopped")
	sys.exit(0)
