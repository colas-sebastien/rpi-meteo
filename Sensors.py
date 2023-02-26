#! /usr/bin/env python
#
# Read data from BeeWi BBW200 readers and record it to MySQL DB
#
# Adapted from :
# https://github.com/enrimilan/BeeWi-BBW200-Reader
#

from reader.GattSensorReader import GattSensorReader
from utils.ParseUtils import ParseUtils
import mariadb, time, configparser

# Sensor read
def getBeeWiInfos(sensorName):
    sensorData="";
    try_count=int(settings.get(sensorName, 'retry'));
    while try_count>0 :
        try:
            sensorReader = GattSensorReader()
            rawData = sensorReader.readRawData(settings.get(sensorName, 'MAC_ADDRESS'),settings.get(sensorName, 'UUID'))
            sensorData = ParseUtils.parseSensorData(rawData.split(" "))
            try_count=0
            # There is a bug in the lib for high humidity
            if (sensorData.humidity>100) :
                sensorData.humidity=100;
        except:
            print(time.strftime("%c") + " : "+sensorName+" Retry "+str(try_count))
            try_count-=1
            if (try_count==0):
                    print("Can't read")
                    
    return sensorData;
        

if __name__ == "__main__":
    # Load configuration files
    settings = configparser.ConfigParser()
    settings._interpolation = configparser.ExtendedInterpolation()
    settings.read('meteo.ini')
  
    # Connection to the database
    cnx = mariadb.connect(user=settings.get('mysql', 'user'), database=settings.get('mysql', 'database'), password=settings.get('mysql', 'password'),host=settings.get('mysql', 'location'))
    cursor = cnx.cursor()
        
    # Loop on sensors
    nbSensors=int(settings.get('sensors', 'number'));
    startId=int(settings.get('sensors', 'start_id'));
    
    for sensorId in range(startId,nbSensors+startId) :
        sensorName='sensor_'+str(sensorId);
        sensorType=settings.get(sensorName, 'type');        
        if(sensorType=="BeeWi") :
            sensorData=getBeeWiInfos(sensorName);
    
        # Insert data into the database
        if(sensorData!="") :
            cursor.execute('INSERT INTO sensor_data (sensor_id,temperature,humidity,battery) VALUES (%s,%s,%s,%s);', (str(sensorId),str(sensorData.temperature),str(sensorData.humidity),str(sensorData.battery))) 
            cnx.commit()            
    
    # Clode DataBase Connection
    cursor.close()
    cnx.close()
