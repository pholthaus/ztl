import logging
logging.basicConfig(level=logging.INFO)

from threading import Thread
from ztl.core.protocol import State, Task


class ExecutableTask(object):

  def execute(self):
    pass

  def status(self):
    return None

  def abort(self):
    return False


class TaskController(object):

  def __init__(self):
    self._current = 0
    self._running = {}

  def init(self, request):
    self._current += 1
    request = Task.decode(request) # should be checked if appropriate here
    specs = self.assign(request["handler"], request["component"], request["goal"])
    self._running[self._current] = TaskExecutor(specs[0], *specs[1:])
    return self._current, "Initiated task '%s' with request: %s" % (self._current, request)

  def status(self, mid, request):
    if mid in self._running:
      state = self._running[mid].state()
      result = self._running[mid].result()
      return state, result
    else:
      return State.REJECTED, "Invalid ID '%s'" % mid

  def abort(self, mid, request):
    if mid in self._running:
      success = self._running[mid].stop()
      state = self._running[mid].state()
      return state, success
    else:
      return State.REJECTED, "Invalid ID '%s'" % mid

  def assign(self, handler, component, goal):
    raise RuntimeError("Function 'assign' not implemented in controller.")


class TaskExecutor(Thread):

  def __init__(self, cls, *parameters):
    Thread.__init__(self)
    self.logger = logging.getLogger(type(cls).__name__)
    self.cls = cls
    self.parameters = parameters
    self.task = None
    self._state = State.INITIATED
    self._result = None
    self._prevent = False
    try:
      self.logger.debug("Initiating task with parameters '%s'...", self.parameters)
      self.task = self.cls(*self.parameters)
      self.start()
    except Exception as e:
      self.logger.debug("Task initialising failed, rejecting task: '%s'", e)
      self._state = State.REJECTED
      self._result = e

  def run(self):
    if not self._prevent:
      self.logger.debug("Accepting and executing task...")
      self._state = State.ACCEPTED
      try:
        self._result = self.task.execute()
        self.logger.debug("Task execution completed successfully.")
        self._state = State.COMPLETED
      except Exception as e:
        self.logger.debug("Task execution failed: '%s'", e)
        self._state = State.FAILED
        self._result = e

    else:
      self._state = State.ABORTED
      logging.warn("Task execution prevented during initialising.")

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
      return success

  def abort(self):
    print("Aborting immediately as requested...")
    self._state = State.ABORTED
    super().abort()

  def state(self):
    if self._state is State.ACCEPTED:
      self._result = self.task.status()
    return self._state

  def result(self):
    return self._result
