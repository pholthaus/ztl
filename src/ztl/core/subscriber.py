import zmq
import logging

from threading import Thread

logging.basicConfig(level=logging.INFO)

class ObjectSubscriber(Thread):
  
  def __init__(self, host, port, scope):
    Thread.__init__(self)
    self.callbacks = {}
    self.client_no = 0
    self.logger = logging.getLogger('object-subscriber')
    context = zmq.Context()
    # self.socket.setsockopt(zmq.RCVHWM, 4)
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
        self.logger.debug("Received object %s, executing callback...", repr(obj))
        self.callback(obj)
    except Exception as e:
      self.logger.error("Listening failed: '%s'", e)
      
    self.active = False
    self.logger.info("Finished listening.")


  def stop(self):
    self.callbacks.clear()
    self.active = False


  def callback(self, obj):
    for client, method in self.callbacks.items():
      self.logger.debug("Executing callback '%s' with '%s'..." % (client, repr(obj)))
      method(obj)


  def register_callback(self, method):
    self.logger.debug("Registering callback client '%s'..." % self.client_no)
    self.callbacks[self.client_no] = method
    self.client_no = self.client_no + 1
    return self.client_no - 1


  def remove_callback(self, client_no):
    self.logger.debug("Removing callback client '%s'..." % client_no)
    del self.callbacks[client_no]
