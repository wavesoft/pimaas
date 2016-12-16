import youtube_dl
from threading import Thread

class AbortError(RuntimeError):
  pass

class YoutubeDownloader:
  """
  """
  def __init__(self, postbox):
    self.postbox = postbox
    self.abortFlag = False
    self.t_ydl = None
    self.startedDownloading = False

  def debug(self, msg):
    self.postbox.send('log', 'debug', msg)

  def warning(self, msg):
    self.postbox.send('log', 'warn', msg)

  def error(self, msg):
    self.postbox.send('log', 'error', msg)

  def callback_hook(self, d):
    if self.abortFlag:
      raise AbortError()

    if d['status'] == 'finished':
      self.postbox.send('progress', 'end')

    elif d['status'] == 'downloading' and not self.startedDownloading:
      self.startedDownloading = True
      self.postbox.send('progress', 'run')

  def ydl_thread(self, video, pipe):
    ydl_opts = {
      'outtmpl': pipe,
      'nopart': True,
      'logger': self,
      'quiet': True,
      'noprogress': True,
      'format': 'mp4',
      'progress_hooks': [self.callback_hook],
    }
    try:
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video])
      self.postbox.send('progress', 'end')
    except AbortError:
      self.postbox.send('progress', 'abort')
    except Exception:
      self.postbox.send('progress', 'error')

    self.t_ydl = None

  def start(self, video, pipe):
    self.postbox.send('progress', 'init')

    self.startedDownloading = False
    self.t_ydl = Thread(target=self.ydl_thread, args=(video, pipe))
    self.t_ydl.start()
    self.postbox.send('progress', 'start')

  def kill(self):
    if not self.t_ydl:
      return

    self.abortFlag = True

  def wait(self):
    if not self.t_ydl:
      return

    self.t_ydl.join()

