#!/bin/bash
cd /home/pi/rpi-meteo
python ./Sensors.py >> Sensors.log 2>&1
