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
    logging.info("Initiating task controller...")
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
      logging.warn("Task execution prevented during controller initialising.")
    return self.state


  def stop(self):
    if self.ctrl is None:
      logging.info("Preventing controller from executing as requested...")
      self.prevent = True
    else:
      logging.info("Aborting execution as requested...")
      self.ctrl.abort()
    self.state = State.ABORTED


  def abort(self):
    logging.info("Aborting immediately as requested...")
    self.state = State.ABORTED
    super().abort()


  def get_state():
    return self.state


class InstantTask(ThreadedTask):

  def stop(self):
    logging.warning("Aborting not supported, ignoring...")
