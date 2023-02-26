#! /usr/bin/env python3
# coding: utf-8 
import configparser
import pygame
import time
import datetime
import mariadb
from pygame.locals import *

def parse_2_values(value_to_split):
    tmp=value_to_split.split(',')
    return((int(tmp[0]),int(tmp[1])))

# Load configuration files
settings = configparser.ConfigParser()
settings._interpolation = configparser.ExtendedInterpolation()
settings.read('meteo.ini')

color_green_lcd=(100,255,145)
color_red_lcd=(255,0,0)
color_blue_lcd=(0,0xfc,0xff)

# Screen display
dimension=parse_2_values(settings.get('display', 'dimension'))
pygame.init()
pygame.mouse.set_visible(0)
screen = pygame.display.set_mode(dimension,(FULLSCREEN if settings.get('display', 'fullscreen')=='true' else RESIZABLE),32)

# Refresh Display
refresh_rate = int(settings.get('display', 'refresh'))
seconds_since_last_refesh = refresh_rate    

# General parameters
url_openweathermap         =             settings.get('openweathermap', 'url')     \
                           + '?id='    + settings.get('openweathermap', 'id')      \
                           + '&units=' + settings.get('openweathermap', 'units')   \
                           + '&APPID=' + settings.get('openweathermap', 'APPID')

# MySQL
mysql_config={
  'user':       settings.get('mysql', 'user'),
  'password':   settings.get('mysql', 'password'),
  'database':   settings.get('mysql', 'database'),  
  'host':       settings.get('mysql', 'location')
}
cnx = mariadb.connect(**mysql_config)

sql_sensor_ext  ='SELECT date,temperature,humidity,battery FROM sensor_data WHERE sensor_id=1 AND date > (NOW() - INTERVAL 15 MINUTE) order by date DESC LIMIT 1'
sql_sensor_int  ='SELECT date,temperature,humidity,battery FROM sensor_data WHERE sensor_id=2 AND date > (NOW() - INTERVAL 15 MINUTE) order by date DESC LIMIT 1'
sql_forecast    ='SELECT icon,date,temperature,humidity FROM meteo.openweathermap WHERE date >  "{DATE}" ORDER BY date ASC LIMIT 1'
sql_forecast_3d ='SELECT icon,date,temperature,humidity FROM meteo.openweathermap WHERE date > ("{DATE}" + INTERVAL 1 DAY) AND (date like "%15:00:00" OR date like "%09:00:00") ORDER BY date ASC LIMIT 6;'

font = pygame.font.Font('font/MeteoFont.ttf', 20)
font_big = pygame.font.Font('font/MeteoFont.ttf', 54)

while True:
    now = datetime.datetime.now()
    
    if(seconds_since_last_refesh >= refresh_rate) :
        forecast_3d_icons=[]
        forecast_icon=[]
        txt_temperature_ext="--.-"
        txt_humidity_ext="---"
        txt_temperature_int="--.-"
        txt_humidity_int="---"
                
        cursor = cnx.cursor()
        
        cursor.execute(sql_sensor_ext)        
        for (date, temperature, humidity, battery) in cursor:
            txt_temperature_ext = "%.1f"%float(temperature) +"°"
            txt_humidity_ext    = "%.0f"%int(humidity) + "%"
            
        cursor.execute(sql_sensor_int)        
        for (date, temperature, humidity, battery) in cursor:
            txt_temperature_int = "%.1f"%float(temperature) +"°"
            txt_humidity_int    = "%.0f"%int(humidity) + "%"            

        midnight_date=now.strftime('%Y-%m-%d 00:00:00');
        
        cursor.execute(sql_forecast.replace('{DATE}',now.strftime('%Y-%m-%d %H:%M:%S')))   
        for (icon,date_forecast,temperature_forecast,humidity_forecast) in cursor:
            forecast_icon.append(icon)
        
        cursor.execute(sql_forecast_3d.replace('{DATE}',midnight_date))   
        for (icon_3d,date_forecast_3d,temperature_forecast_3d,humidity_forecast_3d) in cursor:
            forecast_3d_icons.append(icon_3d)
            
        seconds_since_last_refesh=0
        cursor.close()
        cnx.commit()         
        
    screen.fill((0, 0, 0))    
    
    # DISPLAY FORECAST
    for icon in forecast_icon :
        image_weather = pygame.image.load('img/'+icon+'.png')
        screen.blit(image_weather, (-6, 60))        
    
    # DISPLAY DATE
    label = font.render(settings.get('translation','days').split(',')[datetime.datetime.today().weekday()]+now.strftime('  %d/%m/%Y'), 1, color_green_lcd)        
    screen.blit(label, (int(dimension[0]/2-label.get_width()/2), 2))
    
    # DISPLAY CLOCK
    label = font_big.render(now.strftime('%H:%M'), 1, color_green_lcd)
    screen.blit(label, (90, 30))
    label = font.render(now.strftime('%S'), 1, color_green_lcd)
    screen.blit(label, (240, 64))
    
    # DISPLAY TEMPERATURES
    label = font_big.render(txt_temperature_ext, 1, color_red_lcd)
    screen.blit(label, (dimension[0]-label.get_width()-4, 100))
    
    label = font.render(txt_temperature_int, 1, color_red_lcd)
    screen.blit(label, (dimension[0]-label.get_width()-4, 160))    
    
    # DISPLAY HUMIDITIES
    label = font_big.render(txt_humidity_ext, 1, color_blue_lcd)
    screen.blit(label, (dimension[0]-label.get_width(), 190))    

    label = font.render(txt_humidity_int, 1, color_blue_lcd)
    screen.blit(label, (dimension[0]-label.get_width(), 250))  


    # DISPLAY NEXT 3 DAYS FORECAST
    index=0
    for icon in forecast_3d_icons :      
        image_weather = pygame.image.load('img/'+icon+'_1.png')      
        screen.blit(image_weather, (int((index-(index%2))/2*100+5), 260+(index%2)*116)) 
        if (index%2)==0 :
            label = font.render(settings.get('translation','days').split(',')[(datetime.datetime.today().weekday()+1+int(index/2))%7][:3], 1, color_green_lcd)        
            screen.blit(label, (int(index/2*100+34), 364))
        index+=1         
    
    pygame.display.flip()
    seconds_since_last_refesh+=1
    time.sleep(1)

cnx.close()      
