import zmq
import logging

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
    
  def run(self):
    self.logger.info("Start listening...")
    self.active = True
    try:
      while self.active:
        topic = self.socket.recv_string()
        obj = self.socket.recv_pyobj()
        self.callback(obj)
    except Exception as e:
      self.logger.error("Listening failed: '%s'", e)
      
    self.active = False
    self.logger.info("Finished listening.")
      
  def stop(self):
    self.active = False
    
  def callback(self, obj):
    raise RuntimeError("Function 'callback' not implemented in subscriber.")
