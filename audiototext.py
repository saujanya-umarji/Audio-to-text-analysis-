import os
import pika
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
import pymongo
import base64
import io


app = Flask(__name__)

# defining a route
@app.route("/") 
def home(): 
    return render_template('index.html')
@app.route("/myform")
def form():
    #request.variableName from html page
    return render_template('audiototext.html')


@app.route("/myform1", methods=['POST', 'GET'])
def process():
    #myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    #mydb = myclient["mydatabase"]
    #mycol = mydb["database"]
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    result = ""
    result1 = ""
    result2 = ""
    #data={}
    print(request)
    if request.method == 'POST':
        channel1 = connection.channel()
        #channel1.exchange_declare(exchange='logs', exchange_type='fanout')
        channel1.queue_declare(queue='blob')
        print("the method is post!!!")
        print(request.files)
        
        if 'myFile' in request.files:
            print("yess the myfile is in this!!!")
            
            myFile = request.files['myFile']
            #encode = base64.b64encode(content)
            #print(encode.__len__())
            #data["data"] = encode.decode('ascii') 
            #final_data = json.dumps(contents)
            #final_data = json.loads(final_data)
            #print(final_data.__len__())
            #x = mycol.insert_many(decode)

            #print list of the _id values of the inserted documents:
            #print(x.inserted_ids)
            #content = request.files['myFile'].read()
            print(myFile)
            path=os.path.join('C:/Users/Sunplus/uploads/', myFile.filename)
            print(path)
            print("asxsasassss",myFile.filename )
            if myFile != '': 
                myFile.save(os.path.join('C:/Users/Sunplus/uploads/', myFile.filename))
                # retriveFile(path)
                result=audioText(path)
                result1 = sentiment_analyzer_scores(result)
                result2 = get_word_sentiment(result)
                message = {"result":result,"result1":result1,"result2":result2}
                print(message)
                #channel1.basic_publish(exchange='logs', routing_key='', body=result)
                channel1.basic_publish(exchange='',routing_key='blob',body=json.dumps(message))
                print(" [x] Sent %r" % message)
                connection.close()
                print(result)
                print(result1)
                print(result2)
        else: result = 'error'
        return jsonify(result=result,result1=result1,result2=result2)
    else: return jsonify({"error": "only POST method allowed"}),404

# def retriveFile(path):
#     print("===============inside retrive file==============")
#     print(path)

def audioText(path):
        # filename = 'C:/Users/Sunplus/Anaconda3/Lib/site-packages/speech_recognition/pocketsphinx-data/en-in-8khz/pronounciation-dictionary.dic'
        # commands = {}
       
        # with open(filename) as fh:
        #     for line in fh:
        #         command, description = line.strip().split(' ', 1)
        #         commands[command] = description.strip()
        

        # abc = json.dumps(commands, indent=2, sort_keys=True)
        # f = open("C:/Users/Sunplus/Anaconda3/Lib/site-packages/speech_recognition/pocketsphinx-data/en-in-8khz/pronounciation-dictionary.json","w")
        # f.write(abc)
        # f.close()
        #frame_rate = frame_rate_channel(path)
        #print(frame_rate)
        # audio = sr.AudioData(json_data,8000,1)
        # print("sample rate===",audio.sample_rate)
        # print(audio) 
        audio = AudioSegment.from_file(path, format="wav")
        audio = audio.set_frame_rate(8000)
        audio.export(path, format="wav")
        AUDIO_FILE = path 
        
        r = sr.Recognizer()
        with sr.AudioFile(AUDIO_FILE) as source: 
            audio = r.record(source)
            
            print("sample rate ===:",audio.sample_rate)
            print(audio)
        try: 
            #text = r.recognize_sphinx(audio)
            #text = r.recognize_sphinx(audio,language="en-in-8khz")
            text = r.recognize_google(audio) 
            print(text) 
            return text  
        except sr.UnknownValueError: 
            print(" Speech Recognition could not understand audio")

analyser = SentimentIntensityAnalyzer() 
def sentiment_analyzer_scores(sentence):
        aSnt = analyser.polarity_scores(sentence)
        print("check this===========",aSnt)
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

    #print('Positive:',pos_word_list)        
    #print('Neutral:',neu_word_list)    
    #print('Negative:',neg_word_list)
    return ('''\u2022 Positive words:''',pos_word_list,'''\r\n\u2022 Neutral words: ''',neu_word_list,'''\r\n\u2022 Negative words: ''',neg_word_list)

# def frame_rate_channel(audio_file_name):
#     with wave.open(audio_file_name, 'w') as wave_file:
#         frame_rate = wave_file.setframerate(8000)
#         return frame_rate
app.run(debug=True) 