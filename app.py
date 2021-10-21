import os
import pika
import io
import urllib.request
from flask import Flask, flash, request, redirect, render_template,jsonify
from werkzeug.utils import secure_filename
import speech_recognition as sr
import wave
import json
from pydub import AudioSegment 
import math
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import string
import nltk
from nltk.tokenize import word_tokenize, RegexpTokenizer
from flask_pymongo import PyMongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import gridfs
from io import BytesIO


app = Flask(__name__)
db = MongoClient().pollmonk
fs=gridfs.GridFS(db,"audiofiles")
#rabbitMQ pika connection(AMQP) 
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))


@app.route("/myform")
def form():
    #request.variableName from html page
    return render_template('audiototext.html')

#post method 
@app.route("/myform1", methods=['POST', 'GET'])
def process():
    #creating channel
    channel = connection.channel()
    #declaring a queue
    channel.queue_declare(queue='audioToText')
    if request.method == 'POST':
        print(request.files)
        if 'myFile' in request.files:
            myFile = request.files['myFile'] 
            print(myFile)
            audioId = saveFile(myFile) #function to save data in mongodb
            audioFiles = fs.find_one({ "_id" : ObjectId(audioId)}) #retrieving data from mongodb
            result = audioText(audioFiles) #function to convert to text
            result1 = sentiment_analyzer_scores(result) #function to analyse sentiment score
            result2 = get_word_sentiment(result) #function to get analysed words
            message = {"id":str(audioId),"surveyId":str(audioFiles.surveyId),"result":result,"result1":result1,"result2":result2}
            print(message) 
            channel.basic_publish(exchange='',routing_key='audioToText',body=json.dumps(message)) #sending json data in queue
            print("sent data in rabbitmq channel")
            connection.close()
            print("printing result")
            print(str(result))
            print(result1)
            print(result2)
        else: result = 'error'
        return jsonify(result=result,result1=result1,result2=result2)
    else: return jsonify({"error": "only POST method allowed"}),404

def saveFile(myFile):
    audioId = fs.put(myFile,surveyId = "abcd123456")
    return audioId


def audioText(audioFiles):
        r = sr.Recognizer()
        f = audioFiles
        file_obj = io.BytesIO()  # create file-object
        file_obj.write(f.read()) # write in file-object
        file_obj.seek(0) # move to beginning so it will read from beginning
        mic = sr.AudioFile(file_obj) # use file-object 
        with mic as source:
            audio = r.record(source)
            print("sample rate ===:",audio.sample_rate)
            print(audio)
        try: 
            #text = r.recognize_sphinx(audio)
            #text = r.recognize_sphinx(audio,language="en-in-8khz")
            result = r.recognize_google(audio)
            print(result)
            return result
        except sr.UnknownValueError: 
            print(" Speech Recognition could not understand audio")


analyser = SentimentIntensityAnalyzer() 
def sentiment_analyzer_scores(sentence):
        aSnt = analyser.polarity_scores(sentence)
        print(type(aSnt))
        return aSnt
nltk.download('punkt')
nltk.download('vader_lexicon')
def get_word_sentiment(text):
    tokenized_text = nltk.word_tokenize(text)
    pos_word_list=[]
    neu_word_list=[]
    neg_word_list=[]
    for word in tokenized_text:
        if (analyser.polarity_scores(word)['compound']) >= 0.1:
            pos_word_list.append(word)
        elif (analyser.polarity_scores(word)['compound']) <= -0.1:
            neg_word_list.append(word)
        else:
            neu_word_list.append(word)
    return ('''\u2022 Positive words:''',pos_word_list,'''\r\n\u2022 Neutral words: ''',neu_word_list,'''\r\n\u2022 Negative words: ''',neg_word_list)

app.run(debug=True) 