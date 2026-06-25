import zmq
import logging

import threading

from ztl.core.server import TaskServer
from ztl.core.task import ExecutableTask, TaskController

logging.basicConfig(level=logging.INFO)


class PublisherService(ExecutableTask):
  
    def __init__(self, publisher, goal):
      self.logger = logging.getLogger('publisher-service')
      self.publisher = publisher
      self.goal = goal
      
    def execute(self):
      goal = str(self.goal).lower() in ['true', '1', 't', 'y', 'yes']
      self.publisher.setEnabled(goal)

class PublisherController(TaskController):
  
  def __init__(self, publisher):
    super(PublisherController, self).__init__()
    self.publisher = publisher
    self.logger = logging.getLogger('publisher-controller')
    
  def assign(self, handler, component, goal):
    if handler == "publisher":
      if component == "service":
        return PublisherService, self.publisher, goal
      else:
        self.logger.error("Unknown component: %s" % component)
        raise RuntimeError("Unknown component: %s" % component)    
    else:
      self.logger.error("Unknown handler: %s" % handler)
      raise RuntimeError("Unknown handler: %s" % handler)

class ObjectPublisher(object):

  def __init__(self, port, scope):
    self.logger = logging.getLogger('object-publisher')
    context = zmq.Context()
    self.socket = context.socket(zmq.PUB)
    address = "tcp://*:" + str(port)
    self.socket.bind(address)
    self.scope = scope
    self.logger.info("Publisher '%s' created at '%s'" % (scope, address))
    self.setEnabled(True)
    
    server = TaskServer(port * 2)
    server.register(scope + ":service", PublisherController(self))
    service = threading.Thread(target=server.listen)
    service.start()
    
    
  def publish(self, obj):
    if self.enabled:
      self.logger.info("Publishing %s...", repr(obj))
      self.socket.send_string(self.scope, zmq.SNDMORE)
      self.socket.send_pyobj(obj)
    else:
      self.logger.info("Skipping publishing!")

  def setEnabled(self, enabled):
    self.enabled = enabled
    self.logger.info("Publisher '%s' enabled: '%s'" % (self.scope, enabled))

if __name__ == "__main__":
  
  o = ObjectPublisher(5551, "testy")
