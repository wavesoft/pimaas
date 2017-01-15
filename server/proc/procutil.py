import os
import signal
from select import select
from subprocess import Popen, PIPE
from threading import Thread

class ProcessManager:
  """
  """
  def __init__(self, postbox):
    self.postbox = postbox
    self.t_proc = None
    self.t_monitor = None

    self.stdout_buf = ""
    self.stderr_buf = ""
    self.signal_pipe = None
    self.staredOutput = False

    self.openStdin = False

  def send(self, stdin):
    if not self.openStdin:
      return

    self.t_proc.stdin.write(stdin)
    self.t_proc.stdin.flush()

  def start(self, cmdline, shell=False):
    self.postbox.send('progress', 'init')

    self.staredOutput = False

    stdin = None
    if self.openStdin:
      stdin = PIPE

    try:
      self.t_proc = Popen(cmdline, stdout=PIPE, stderr=PIPE, stdin=stdin,
        bufsize=1, preexec_fn=os.setsid, shell=shell)
    except Exception:
      self.postbox.send('progress', 'start')
      self.postbox.send('progress', 'abort')
      return

    self.t_monitor = Thread(target=self.monitor_thread)
    self.t_monitor.daemon = True
    self.t_monitor.start()
    self.postbox.send('progress', 'start')

  def monitor_thread(self):

    # Create a signal pipe
    (signal, self.signal_pipe) = os.pipe()

    # This loop will stay alive as long as the process is there
    while True:
      rlist, wlist, xlist = [self.t_proc.stdout, self.t_proc.stderr, signal], [], []
      rlist, wlist, xlist = select(rlist, wlist, xlist)

      if self.t_proc.stdout in rlist:
          out = os.read(self.t_proc.stdout.fileno(), 1024)
          if not out:
              break

          if not self.staredOutput:
            self.postbox.send('progress', 'run')
            self.staredOutput = True

          self.stdout_buf += out
          while '\n' in self.stdout_buf:
            line, self.stdout_buf = self.stdout_buf.split('\n', 1)
            self.postbox.send('log', 'info', line)

      if self.t_proc.stderr in rlist:
          out = os.read(self.t_proc.stderr.fileno(), 1024)
          if not out:
              break

          if not self.staredOutput:
            self.postbox.send('progress', 'run')
            self.staredOutput = True

          self.stderr_buf += out
          while '\n' in self.stderr_buf:
            line, self.stderr_buf = self.stderr_buf.split('\n', 1)
            self.postbox.send('log', 'error', line)

      if signal in rlist:
        break

    # Close STDOUT
    os.close(signal)
    os.close(self.signal_pipe)
    self.t_proc.stdout.close()
    self.t_proc.stderr.close()

    # Close STDIN
    if self.openStdin:
      self.t_proc.stdin.flush()
      self.t_proc.stdin.close()

    # Trigger completion according to exit code
    ret = self.t_proc.wait()
    if ret == 0:
      self.postbox.send('progress', 'end')
    else:
      self.postbox.send('progress', 'error', 'Process exited with %i' % ret)

  def kill(self):
    if not self.t_proc:
      return

    # Signal the pipe to exit the select() loop
    try:
      os.write(self.signal_pipe, '\n')
    except Exception:
      pass

    # Kill process group
    try:
      os.killpg(os.getpgid(self.t_proc.pid), signal.SIGTERM)
    except Exception:
      pass

  def wait(self):
    if not self.t_proc:
      return

    # t_monitor does a t_proc.wait()
    self.t_monitor.join()
