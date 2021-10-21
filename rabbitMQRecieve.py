import os
import pika
import io
import urllib.request
from flask import Flask, flash, request, redirect, render_template,jsonify
import sys
import json

app = Flask(__name__)

def process():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel1 = connection.channel()
    channel1.queue_declare(queue='audioToText')
    def callback(ch, method, properties, body):
        print(" [x] Received %r",body)
        retriveData(body)
    channel1.basic_consume(queue='audioToText', on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel1.start_consuming()
    print(request) 

def retriveData(body):
    print("heyyy u are inside the data...")
    print(body)
    messages = json.loads(body)
    print(messages["surveyId"])

app.run(debug=True,redirect=process()) 


