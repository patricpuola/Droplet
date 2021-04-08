#!/usr/bin/python3
# Program: Droplet Irrigation system 0.1
# Author: Patric Puola
import sys
import conf
import os
from db import DropletDB

flags = sys.argv

activated_triggers = DropletDB.getActivatedTriggers()

pump_script = str(conf.ROOT / "run_pump.py")

for trigger in activated_triggers:
	pump_pin = DropletDB.getPumpPin(trigger['pump_id'])
	print("Trigger #"+str(trigger['id'])+" activated from sensor "+str(trigger['sensor_id']))
	print("pump "+str(trigger['pump_id'])+" (pin "+str(pump_pin)+"), "+str(trigger['amount_ml'])+"ml")
	os.system(pump_script+" "+str(pump_pin)+" "+str(trigger['amount_ml']))
	DropletDB.logIrrigation(trigger['pump_id'], trigger['amount_ml'])
