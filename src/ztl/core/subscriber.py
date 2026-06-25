import zmq
import logging

from ztl.core.client import RemoteTask
from ztl.core.protocol import State, Task

from threading import Thread

logging.basicConfig(level=logging.INFO)

class ObjectSubscriber(Thread):
  
  def __init__(self, host, port, scope):
    Thread.__init__(self)
    self.logger = logging.getLogger('object-subscriber')
    context = zmq.Context()
    self.socket = context.socket(zmq.SUB)
    address = "tcp://" + str(host) + ":" + str(port)
    self.socket.connect(address)
    self.socket.setsockopt_string(zmq.SUBSCRIBE, scope)
    self.logger.info("Subscriber '%s' established at '%s'" % (scope, address))
    self.active = False
    self.service = RemoteTask(host, port * 2, scope + ":service")
    
  def run(self):
    
    mid, reply = self.service.trigger(Task.encode("publisher", "service", True))
    state, reply = self.service.wait(mid)
    if state == State.COMPLETED and reply == "True":
      self.logger.info("Start listening...")
      self.active = True
      try:
        while self.active:
          topic = self.socket.recv_string()
          obj = self.socket.recv_pyobj()
          self.callback(obj)
      except Exception as e:
        self.logger.error("Listening failed: '%s'", e)
        
      self.service.trigger(Task.encode("publisher", "service", False))
      self.active = False
      self.logger.info("Finished listening.")
    else:
      self.logger.info("Publisher not avaliable for service requests.")
      
  def stop(self):
    self.active = False
    
  def callback(self, obj):
    raise RuntimeError("Function 'callback' not implemented in subscriber.")
