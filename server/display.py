import socket
from .ui.frontend import Frontend
from .util.messenger import MessengerListener

MODE_WELCOME = 0
MODE_IDLE = 1
MODE_LOADING = 2
MODE_ERROR = 3

class Display(MessengerListener):
  def __init__(self, messenger):
    self.messenger = messenger
    self.messenger.addListener(self)

    self.display = Frontend()
    self.setMode(MODE_WELCOME)

  def wakeup(self):
    with open('/dev/tty1', 'a') as f:
      f.write('\033[9;0]')

  def cleanup(self):
    self.display.setActive(False)

  def setMode(self, mode):
    self.wakeup()

    if mode == MODE_WELCOME:
      self.display.setImage(0)
      self.display.setTitle('Grab your phone')
      self.display.setSubTitle('And connect to http://%s.local:8080' % socket.gethostname())
      self.display.update()

    elif mode == MODE_IDLE:
      self.display.setImage(0)
      self.display.setTitle('Grab your phone')
      self.display.setSubTitle('And connect to http://%s.local:8080' % socket.gethostname())
      self.display.update()

    elif mode == MODE_LOADING:
      self.display.setImage(3)
      self.display.setTitle('Downloading Media')
      self.display.setSubTitle('Hold on, this might take a few seconds')
      self.display.update()

    elif mode == MODE_ERROR:
      self.display.setImage(2)
      self.display.setTitle('Something went wrong')
      self.display.update()

  def setThumbnail(self, image):
    self.display.setImage(3)
    self.display.setTitle('Downloading Media')
    self.display.setSubTitle('Hold on, this might take a few seconds')
    self.display.update()

    if image:
      self.display.setThumbImage(image)


  def handleMessage(self, source, event, args):
    # Turn on when video queue is empty
    if source == 'video':
      if event == 'queue':
        if args[0] == 'empty':
          self.display.setActive(True)
          self.setMode(MODE_IDLE)
        elif args[0] == 'start':
          self.display.setActive(True)
          self.setMode(MODE_LOADING)

    # Turn on right before video player starts
    if source == 'video.player':
      if event == 'progress':
        if args[0] == 'run':
          self.display.setActive(False)

    # Show results on display
    if event == 'log':
      self.display.setSubTitle('[%s.%s]: %s' % (source, args[0], args[1]))
      self.display.update()

    # Show error screen on errors
    if event == 'progress' and args[0] == 'error':
      self.setMode(MODE_ERROR)
