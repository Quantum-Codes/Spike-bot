from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def lol():
  return "Hello..."
  
def run():
  app.run("0.0.0.0",port=8080)

def keep_alive():
  t1 = Thread(target=run).start()