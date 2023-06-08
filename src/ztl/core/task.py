import time
import logging
logging.basicConfig(level=logging.INFO)

from threading import Thread
from ztl.core.protocol import State

class ExecutableTask(object):

  def initialise(self):
    return True


  def execute(self):
    return True


  def abort(self):
    return True


class TimedTask(ExecutableTask):

  def __init__(self, duration):
    self.active = True
    self.duration = duration

  def initialise(self):
    return True

  def execute(self):
    start = time.time()
    while self.active and time.time() - start < self.duration:
      time.sleep(.1)
    return self.active

  def abort(self):
    self.active = False
    return True


class TaskExecutor(Thread):

  def __init__(self, cls, *parameters):
    Thread.__init__(self)
    self.logger = logging.getLogger(type(cls).__name__)
    self.cls = cls
    self.parameters = parameters
    self.task = None
    self._state = State.INITIATED
    self._prevent = False
    self.start()


  def run(self):
    self.logger.debug("Initiating task with parameters '%s'...", self.parameters)
    self.task = self.cls(*self.parameters)
    success = self.task.initialise()
    if success:
      if not self._prevent:
        self.logger.debug("Accepting and executing task...")
        self._state = State.ACCEPTED
        success = self.task.execute()
        if success:
          self.logger.debug("Task execution completed successfully.")
          self._state = State.COMPLETED
        else:
          self.logger.debug("Task execution failed.")
          self._state = State.FAILED
      else:
        self._state = State.FAILED
        logging.warn("Task execution prevented during initialising.")
    else:
      self.logger.debug("Task initialising failed, rejecting task.")
      self._state = State.REJECTED


  def stop(self):
    if self.task is None:
      self.logger.debug("Preventing task from executing...")
      self._prevent = True
      self._state = State.ABORTED
    else:
      self.logger.debug("Aborting task execution...")
      success = self.task.abort()
      if success:
        print("Task aborted successfully.")
        self._state = State.ABORTED
      else:
        self.logger.debug("Task could not be aborted.")
    return self._state


  def abort(self):
    print("Aborting immediately as requested...")
    self._state = State.ABORTED
    super().abort()


  def state(self):
    return self._state


class SimpleTaskHandler(object):

  def __init__(self):
    self.current_id = 0
    self.running = {}

  def init(self, payload):
    self.current_id += 1
    print("Initialising Task ID '%s' (%s)..." % (self.current_id, payload))
    self.running[self.current_id] = TaskExecutor(TimedTask, int(payload))
    return self.current_id, ""

  def status(self, mid, payload):
    if mid in self.running:
      print("Status Task ID '%s' (%s)..." % (mid, payload))
      return self.running[mid].state(), mid 
    else:
      return State.REJECTED, "Invalid ID"


  def abort(self, mid, payload):
    if mid in self.running:
      print("Aborting Task ID '%s' (%s)..." % (mid, payload))
      return self.running[mid].stop(), mid
    else:
      return State.REJECTED, "Invalid ID"


