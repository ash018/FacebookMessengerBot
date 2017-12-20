import os
import sys
import json
from datetime import datetime
from pymessenger import Bot
import requests
from flask import Flask, request
from fbmq import Page
from utils import wit_response,get_news_elements
from weatherApi import data_output,data_organizer,data_fetch,url_builder

app = Flask(__name__)


PAGE_ACCESS_TOKEN = "EAAbv9xxXgOMBAO7E1ViMxKXQULbofIvX7WyfZA26ZC9jitnS6w3PzDsGAkh4sn4f4C84tEhvr54rJFM4mA5lfE0hLxuWXXtdcM8QjhU6cxL75oH1PJWyEAIrfZAPMoxcFPXBZCIsIPZAom1oKLv79w3oNZCM7Uo1jruudndd7UiRKZCZAkBI3EKB"
bot = Bot(PAGE_ACCESS_TOKEN)
page = Page(PAGE_ACCESS_TOKEN)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world!!!--PyMessenger", 200


@app.route('/', methods=['POST'])
def webhook():
		
		page.handle_webhook(request.get_data(as_text=True) or 'UTF-8')
		print(request.get_json())
		data = request.get_json()
		#log(data)
		print(data)
		
		if data['object'] == 'page':
			for entry in data['entry']:
				for messaging_event in entry['messaging']:

					# IDs
					sender_id = messaging_event['sender']['id']
					recipient_id = messaging_event['recipient']['id']

					if messaging_event.get('message'):
						# Extracting text message
						if 'text' in messaging_event['message']:
							messaging_text = messaging_event['message']['text']
						else:
							messaging_text = 'no text'
						
						'''
						entity, value = wit_response(messaging_text)
						response = ''
						if entity=='newstype':
							response = "Ok I will send you {} news".format(str(value))
						if entity == None:
						 	response = "Welcome Sir, How I can help you ?"
						'''

						categories,value = wit_response(messaging_text)
						elements = get_news_elements(categories)
						#weatherElements = {'temp':None,'humidity':None}
						
							

						response=''
						# if value != None:
						if (categories['newstype']!= None and categories['location']==None):
							response = "Ok I will send you {} news".format(str(value))
							bot.send_text_message(sender_id,response)
							bot.send_generic_message(sender_id, elements)

						elif (categories['newstype']!= None and categories['location']!=None):
							response = "Ok I will send you {} news".format(str(value))
							bot.send_text_message(sender_id,response)
							bot.send_generic_message(sender_id, elements)
						
						elif(categories['weatherinfo']!=None and categories['location']==None):
							response="Current Temperature " + str(weatherElements['temp'])
							bot.send_text_message(sender_id,response)
						
						elif(categories['weatherinfo']!=None and categories['location']!=None):
							print(value[:-2])
							print(categories['location'])
							weatherElements = data_organizer(data_fetch(url_builder(str(categories['location']))))
							print(weatherElements)
							lenWeatherElements  = len(weatherElements.keys())
							#if(weatherElements!=None and lenWeatherElements!=0):
							response= (categories['location']+"'s Temperature is: " +str(weatherElements['temp']) +"\n"+"Humidity is: "+  str(weatherElements['humidity'])+"\nWind Speed is: "+ str(weatherElements['wind'])
												+"\nPressure: "+
										   str(weatherElements['pressure'])+"\nSunrise at: "+
										   str(weatherElements['sunrise'])+"\nSunset at: "+
										   str(weatherElements['sunset'])

								)

							bot.send_text_message(sender_id,response)
							#else:
								#response="Please Enter A City Name"
								#bot.send_text_message(sender_id,response)
							
						
						else:
							response = "Welcome Sir, How I can help you ?"
							bot.send_text_message(sender_id,response)
						
						
						# # Echo
						# response = None
						# entity, value = wit_response(messaging_text)
						# if entity=='newstype':
						# 	response = "Ok I will send you {} news".format(str(value))
						# elif entity == "location":
						# 	response = "Ok, I will send you top headlines from {0}".format(str(value))
						# if entity == None:
						# 	response = "Welcome Sir, How I can help you ?"
						# url = "https://www.youtube.com/watch?v=ru_jQk086sE"	
						#bot.send_text_message(sender_id, response)
						#bot.send_video_url(sender_id,url)
						#bot.send_image(sender_id,'C:\\Users\Akash\Downloads\ACI-Logo.png')
		
		
		return "ok", 200
		

    

def log(message):
	print(message)
	sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True,port=81)
