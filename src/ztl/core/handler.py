import logging

from ztl.core.protocol import State

class ThreadedTask(Thread):

  def __init__(self, client, *parameters):
    Thread.__init__(self)
    self.ctrl = None
    self.prevent = False
    self.client = client
    self.parameters = parameters
    self.state = State.INITIATED
    self.start()


  def run(self):
    logging.info("Initiating task...")
    self.ctrl = self.client(*self.parameters)
    if not self.prevent:
      logging.info("Accepting and executing task...")
      self.state = State.ACCEPTED
      success = self.ctrl.execute()
      if success:
        logging.info("Task completed successfully.")
        self.state = State.COMPLETED
      else:
        logging.info("Task failed.")
        self.state = State.FAILED
    else:
      self.state = State.FAILED
      logging.warn("Task execution prevented during initialising.")
    return self.state


  def stop(self):
    if self.ctrl is None:
      logging.info("Preventing task from executing...")
      self.prevent = True
      self.state = State.ABORTED
    else:
      logging.info("Aborting task execution...")
      success = self.ctrl.abort()
      if success:
        logging.info("Task aborted successfully.")
        self.state = State.ABORTED
      else:
        logging.warning("Task could not be aborted.")


  def abort(self):
    logging.info("Aborting immediately as requested...")
    self.state = State.ABORTED
    super().abort()


  def get_state():
    return self.state


class InstantTask(ThreadedTask):

  def stop(self):
    logging.warning("Aborting not supported, ignoring...")


class Task(object):

  def execute(self):
    return True


  def abort(self):
    return True
