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


class TaskController(object):

  def init(self, payload):
    return -1, "Not implemented"


  def status(self, mid, payload):
      return State.REJECTED, "Not implemented"


  def abort(self, mid, payload):
    return State.REJECTED, "Not implemented"


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
