import os
import tempfile
from .util.messenger import MessengerListener
from .proc.omx import OMXPlayer
from .proc.curl import CURLDownloader
from .proc.playlist import PlaylistDownloader
from .proc.youtube import YoutubeDownloader

PLAYLIST_EXTENSIONS = [ 'm3u', 'm3u8' ]

class EndDetector(MessengerListener):
  def __init__(self, onEnd):
    self.playerStatus = 'idle'
    self.networkStatus = 'idle'
    self.onEnd = onEnd

  def reset(self):
    self.playerStatus = 'idle'
    self.networkStatus = 'idle'

  def isCompleted(self):
    return ((self.playerStatus == 'end') or \
            (self.playerStatus == 'abort') or \
            (self.playerStatus == 'error')) and \
           ((self.networkStatus == 'end') or \
            (self.networkStatus == 'abort') or \
            (self.networkStatus == 'error'))

  def handleMessage(self, source, event, args):
    if event == 'progress':
      if source == 'video.player':
        self.playerStatus = args[0]
      if source == 'video.network':
        self.networkStatus = args[0]

      if self.isCompleted():
        self.onEnd()

class VideoSession:
  def __init__(self, video, url, direct):
    self.url = url
    self.direct = direct
    self.killing = False

    # Create new random file
    (fd, tmppath) = tempfile.mkstemp()
    os.close(fd)
    os.unlink(tmppath)

    # Create fifof
    os.mkfifo(tmppath)
    self.fifoFile = unicode(tmppath)

    # Create the process engines
    self.proc_player = OMXPlayer(video.messenger.getPostbox('video.player'))
    if direct:
      self.proc_network = CURLDownloader(video.messenger.getPostbox('video.network'))
    else:
      if url.split('?')[0].split('.')[-1].lower() in PLAYLIST_EXTENSIONS:
        self.proc_network = PlaylistDownloader(video.messenger.getPostbox('video.network'))
      else:
        self.proc_network = YoutubeDownloader(video.messenger.getPostbox('video.network'))

  def start(self):
    # Start
    self.proc_network.start(self.url, self.fifoFile)
    self.proc_player.start(self.fifoFile)

  def kill(self):
    # Send kill signal
    self.killing = True
    self.proc_network.kill()
    self.proc_player.kill()

  def reap(self):
    # Join
    self.proc_player.wait()
    self.proc_network.wait()

    # Cleanup fifo
    if os.path.exists(self.fifoFile):
      os.unlink(self.fifoFile)

  def control(self, stdin):
    self.proc_player.send(stdin)

class VideoPlayer:
  def __init__(self, messenger):
    self.messenger = messenger
    self.session = None
    self.queue = None

    # Create a messaging source
    self.postbox = self.messenger.getPostbox('video')

    # Listen for progress events and detect clean completions
    self.endDetector = EndDetector(self._handleEnd)
    self.messenger.addListener(self.endDetector)

  def _handleQueueNext(self):
    if self.queue:
      (url, direct) = self.queue
      self.queue = None
      self.postbox.send('queue', 'start', url)
      self._startSession(url, direct)
    else:
      self.postbox.send('queue', 'empty')

  def _handleEnd(self):
    if self.session:
      self._cleanSession()
    self._handleQueueNext()

  def _cleanSession(self):
    self.session.reap()
    self.session = None

  def _startSession(self, url, direct):
    self.session = VideoSession(self, url, direct)
    self.session.start()

  def play(self, url, direct=False):
    self.queue = (url, direct)

    if self.session:
      # Stop previous session and wait for _handleEnd
      if not self.session.killing:
        self.session.kill()
    else:
      self._handleQueueNext()

  def stop(self):
    if self.session and not self.session.killing:
      self.session.kill()

  def control(self, stdin):
    if self.session:
      self.session.control(stdin)

  def getStatus(self):
    ans = {
      'components': {
        'network': self.endDetector.networkStatus,
        'player': self.endDetector.playerStatus
      },
      'video': None
    }

    if self.session:
      ans['video'] = self.session.url

    return ans
