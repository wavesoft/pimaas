from .procutil import ProcessManager

class OMXPlayer(ProcessManager):
  """
  """
  def __init__(self, postbox):
    ProcessManager.__init__(self, postbox)
    self.openStdin = True

  def start(self, pipe):
    ProcessManager.start(self, [
        '/usr/bin/omxplayer', '-I', '-o', 'hdmi', '-w', pipe
      ])
