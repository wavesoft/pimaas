from .procutil import ProcessManager

class PlaylistDownloader(ProcessManager):
  """
  """
  def start(self, url, pipe):
    ProcessManager.start(self, [
        '/usr/bin/avconv', '-y', '-i', url,
        '-f', 'mp4', '-movflags', 'isml+frag_keyframe',
        '-vcodec', 'copy', '-strict', 'experimental', pipe
      ])
