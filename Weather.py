#! /usr/bin/env python3
# coding: utf-8 

import configparser
import urllib.request
import json
import datetime
import mariadb

	     
if __name__ == "__main__":	
	sql='REPLACE INTO openweathermap VALUES (date,temperature,pressure,humidity,icon);'

	# Load configuration files
	settings = configparser.ConfigParser()
	settings._interpolation = configparser.ExtendedInterpolation()
	settings.read('meteo.ini')

	# General parameters
	url_openweathermap         =             settings.get('openweathermap', 'url')     \
							   + '?id='    + settings.get('openweathermap', 'id')      \
							   + '&units=' + settings.get('openweathermap', 'units')   \
							   + '&APPID=' + settings.get('openweathermap', 'APPID')

	try:
		webURL = urllib.request.urlopen(url_openweathermap)
		data = webURL.read()
		encoding = webURL.info().get_content_charset('utf-8')
		infos=json.loads(data.decode(encoding))
	except:
		print("error reading sensor "+url);
		exit(1)

	cnx = mariadb.connect(user=settings.get('mysql', 'user'), database=settings.get('mysql', 'database'), password=settings.get('mysql', 'password'))
	cursor = cnx.cursor()
    
	for item in infos["list"]:		
		date=item["dt_txt"]                
		icon=item["weather"][0]["icon"]
		temperature=item["main"]["temp"]
		humidity=item["main"]["humidity"]	
		pressure=item["main"]["pressure"]  
		cursor.execute('REPLACE INTO openweathermap VALUES (%s,%s,%s,%s,%s);', (date,str(temperature),str(pressure),str(humidity),icon)) 
		
	cnx.commit()
	cursor.close()
	cnx.close()
