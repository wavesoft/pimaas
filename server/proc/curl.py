from .procutil import ProcessManager

class CURLDownloader(ProcessManager):
  """
  """
  def start(self, url, pipe):
    ProcessManager.start(self, [
        '/usr/bin/curl', '-s', '-o', pipe, url
      ])
