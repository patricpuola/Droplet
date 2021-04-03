#!/usr/bin/python3

# Program: Droplet Irrigation system 0.1
# Author: Patric Puola

flags = sys.argv

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
print("start")

def main():
	while True:
#		GPIO.output(12, True)
#		GPIO.output(16, False)
		print("1")
		time.sleep(0.5)
		GPIO.output(12, False)
		GPIO.output(16, True)
		print("2")
		time.sleep(0.5)

try:
	main()
except KeyboardInterrupt:
	GPIO.cleanup()
	print("Droplet stopped")
	sys.exit(0)
