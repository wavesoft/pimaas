from multiprocessing import Queue
from threading import Thread

class MessengerPostbox:
  def __init__(self, messenger, source):
    """
    Initialize a message feeder bound to a messenger and source
    """
    self.messenger = messenger
    self.source = source

  def send(self, key, *args):
    self.messenger.send(self.source, key, args)

class MessengerListener:
  def handleMessage(self, source, event, args):
    pass

class Messenger:
  def __init__(self):
    """
    Initialize
    """
    self.isActive = True
    self.queue = Queue()
    self.thread = Thread(target=self._messengerThreadMain)
    self.listeners = []

    self.start()

  def start(self):
    """
    """
    self.thread.start()

  def stop(self):
    """
    Stop messenger thread
    """
    self.isActive = False
    self.send(None, None, None)
    self.thread.join()

  def getPostbox(self, source):
    """
    Get a new messenger item
    """
    return MessengerPostbox(self, source)

  def addListener(self, listener):
    """
    """
    self.listeners.append(listener)

  def removeListener(self, listener):
    """
    """
    if not listener in self.listeners:
      return
    self.listeners.remove(listener)

  def _messengerThreadMain(self):
    """
    Wait for messages in the queue
    """
    while True:
      message = self.queue.get()
      if not sefl.isActive:
        return
      self.handle(message[0], message[1], message[2])

  def send(self, source, event, args):
    """
    Enqueue event
    """
    self.queue.put((source, event, args))

  def handle(self, source, event, args):
    """
    Handle an event
    """
    for listener in self.listeners:
      listener.handleMessage(source, event, args)
