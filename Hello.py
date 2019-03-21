from flask import Flask, redirect, url_for, request, render_template
from spotipy.oauth2 import SpotifyClientCredentials
import json
import spotipy
import time
import sys
import os
import numpy as np, scipy as sp, librosa, sklearn
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/audio/'
ALLOWED_EXTENSIONS = set(['wav'])

# get audio analysis information for a given song
client_credentials_manager = SpotifyClientCredentials(client_id='d2bde8ff945e4fd9809b5a855ad63cc0',client_secret='22afc78a96a845a7a44f0c1ecbbf3d73')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def getSpotifyID(name,artist):
	query='track:'+name+' AND artist:'+artist
	test=sp.search(q=query,type='track',limit=1)
	if test['tracks']['total']==0:
		print("no result from Spotify")
		return -1
	idn=test['tracks']['items'][0]['id']
	return idn



def getFeatures(name,artist):
	spotID=getSpotifyID(name,artist)
	if spotID==-1:
		return -1
	features = sp.audio_features(spotID)
	score=0.5*features[0]['valence']+0.25*features[0]['danceability']+0.25*features[0]['energy']
	ans={'score':score,'tempo':features[0]['tempo']}
	return ans
def getBeatTimes(name,temp):
    happy, sr = librosa.load('./static/audio/user.wav', duration=30)
    hop = 128
    tempo, beat_frames = librosa.beat.beat_track(happy, sr, hop_length=hop, start_bpm=temp, tightness=200)
    beat_times = librosa.frames_to_time(beat_frames, hop_length=hop, sr=sr)
    return beat_times.tolist()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
   return render_template("index.html")


@app.route('/js/<path:path>')
def send_js(path): return send_from_directory('js', path)

@app.route("/upload")
def upload_file():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def uploader_file():
   if request.method == 'POST':
      f = request.files['file']
      filename=secure_filename('user.wav')
      f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      print("uploaded")
   return "<html>\
      <body>\
         <form action = \"http://localhost:5000/userSong\" method = \"post\">\
            <p>Enter Song Title:<input type = \"text\" name = \"name\" /></p>\
            <p>Enter Artist:<input type = \"text\" name = \"artist\" /></p>\
            <p><input type = \"submit\" value = \"submit\" /></p>\
         </form>\
         <a href=\"/\">Home</a>\
      </body>\
   </html>"

@app.route('/userSong',methods = ['POST', 'GET'])
def login():
   if request.method == 'POST':
      name = request.form['name']
      artist=request.form['artist']
      result_dic=getFeatures(name,artist)
      beats=getBeatTimes(name,result_dic['tempo'])
      data = {'score': result_dic['score'], 'tempo': result_dic['tempo'],'beats':beats}
      return render_template('main.html', data=data)
      return json.dumps(result_dic)

   else:
      # user = request.args.get('nm')
      return "Hello"

if __name__ == '__main__':
   app.run(debug = True)
