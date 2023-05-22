import logging

class ThreadedTask(Thread):

  def __init__(self, client, *parameters):
    Thread.__init__(self)
    self.ctrl = None
    self.prevent = False
    self.client = client
    self.parameters = parameters
    self.start()

  def run(self):
    logging.info("Creating controller...")
    self.ctrl = self.client(*self.parameters)
    if not self.prevent:
      logging.info("Executing...")
      self.ctrl.execute()
    else:
      logging.warn("Execution prevented during controller creation.")

  def stop(self):
    if self.ctrl is None:
      logging.info("Preventing controller from executing as requested...")
      self.prevent = True
    else:
      logging.info("Aborting execution as requested...")
      self.ctrl.abort()

class InstantTask(ThreadedTask):

  def stop(self):
    logging.warning("Aborting not supported, ignoring...")
