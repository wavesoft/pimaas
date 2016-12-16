from .procutil import ProcessManager

class OMXPlayer(ProcessManager):
  """
  """
  def start(self, pipe):
    ProcessManager.start(self, [
        '/usr/bin/omxplayer', '-I', '-o', 'hdmi', '-w', pipe
      ])
