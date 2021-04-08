#!/usr/bin/python3

# Program: Droplet Irrigation system 0.1
# Author: Patric Puola

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
GPIO.output(12, False)
GPIO.output(16, False)
GPIO.output(20, False)
GPIO.output(21, False)

GPIO.cleanup()
sys.exit(0)