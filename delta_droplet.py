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


print("Droplet started")


try:
	if sys.argv[1]:
		pin = int(sys.argv[1])
except IndexError:
	print("Pin not given")
	sys.exit(1)

SPI_PORT = 0
SPI_DEVICE = 0

spi = spidev.SpiDev()
spi.open(SPI_PORT, SPI_DEVICE)
spi.max_speed_hz = 1350000

def mapValue(value, in_min = 0, in_max = 1024, out_min = 0, out_max = 100, precision = 2):
	in_min = float(in_min)
	in_max = float(in_max)
	out_min = float(out_min)
	out_max = float(out_max)

	in_range = in_max-in_min
	out_range = out_max-out_min
	multiplier = out_range/in_range

	return round(((value-in_min)*multiplier)+out_min,precision)


def analogInput(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

def main():
	while True:
		input_value = analogInput(pin)
		print(mapValue(input_value))
		time.sleep(0.2)

try:
	main()
except KeyboardInterrupt:
	spi.close()
	print("Droplet stopped")
	sys.exit(0)
