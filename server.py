#!/usr/bin/env python
print "Hold on, this will take a while..."

# Importing will take some time
import json
import sys
from flask import Flask, request
from server import messenger
from server.video import VideoPlayer
from server.display import Display
from server.util.messenger import MessengerListener

video = VideoPlayer(messenger)
display = Display(messenger)

class Tap(MessengerListener):
  def handleMessage(self, source, event, args):
    print "[%s][%s]: %s" % (source, event, ', '.join(args))

messenger.addListener(Tap())

app = Flask(__name__)

PLAY_PROMPT = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>Play Video</title>
  </head>
  <body>
    <form action="/play" method="POST">
      <p>Video: <input name="video" /></p>
      <p>
        <input type="submit" value="Play" />
        <a href="/stop">Stop</a>
      </p>
    </form>
  </body>
</html>
"""

@app.route("/")
def hello():
  return PLAY_PROMPT

@app.route("/play", methods=['POST'])
def play():

  # Look either in JSON or in form data
  lookIn = request.json
  if not lookIn:
    lookIn = request.form

  # Extract properties
  thumb = None
  direct = False
  if 'thumb' in lookIn:
    thumb = lookIn['thumb']
  if 'direct' in lookIn:
    direct = lookIn['direct']

  display.setThumbnail(thumb)

  video.play(lookIn['video'], direct)
  return json.dumps({'status': 'ok'})

@app.route("/stop")
def stop():
  video.stop()
  return json.dumps({'status': 'ok'})

@app.route("/status")
def status():
  return json.dumps(video.getStatus())

@app.route("/discover")
def discover():
  return json.dumps({
    'version': '0.1.0'
  })

@app.route("/control")
def control():
  keys = request.args.get('keys', None)
  if keys is None:
    return json.dumps({'status': 'missing-keys'})

  try:
    expr = ''.join(map(lambda x: chr(int(x)), keys.split(',')))
  except Exception as e:
    return json.dumps({'status': 'invalid-format'})

  video.control(expr)

  return json.dumps({'status': 'ok'})

@app.route("/exit")
def exit():
  display.cleanup()
  messenger.stop()
  sys.exit(0)

if __name__ == "__main__":
  app.run(
    host="0.0.0.0",
    port=int("80")
  )
