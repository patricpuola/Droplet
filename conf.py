import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

SENSOR_TYPE_UNDEFINED = 0
SENSOR_TYPE_HUMIDITY = 1
SENSOR_TYPE_BRIGHTNESS = 2

SENSOR_BASIL = 1
SENSOR_PEPPERMINT = 2

PIN_BASIL = 7
PIN_PEPPERMINT = 6

PIN_PUMP_BASIL = 16
PIN_PUMP_PEPPERMINT = 12