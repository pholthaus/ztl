import zmq
import logging

from threading import Thread
from zmq.utils.monitor import parse_monitor_message

logging.basicConfig(level=logging.INFO)


class ConnectionTracker(Thread):
  
  subscribers = 0
  active = True
  
  
  def __init__(self, monitor):
    Thread.__init__(self)
    self.monitor = monitor
    self.logger = logging.getLogger('object-publisher')
    
    
  def get_subscribers(self):
    return self.subscribers
    
  
  def run(self):
    while self.active:
      while self.monitor.poll(timeout=10):  # 10ms timeout
          event = parse_monitor_message(self.monitor.recv_multipart())
          if event['event'] == zmq.EVENT_ACCEPTED:
              self.subscribers = self.subscribers + 1
              self.logger.info("Subscriber joined! Total connected: %s", self.subscribers)
              
          elif event['event'] == zmq.EVENT_DISCONNECTED:
              self.subscribers = max(0, self.subscribers - 1)
              self.logger.debug("Subscriber left! Total connected: %s", self.subscribers)
              

class ObjectPublisher(object):

  def __init__(self, port, scope):
    self.logger = logging.getLogger('object-publisher')
    context = zmq.Context()
    self.socket = context.socket(zmq.PUB)
    address = "tcp://*:" + str(port)
    self.socket.bind(address)
    self.scope = scope
    self.subscribers = 0
    
    monitor = self.socket.get_monitor_socket(zmq.EVENT_ACCEPTED | zmq.EVENT_DISCONNECTED)
    self.tracker = ConnectionTracker(monitor)
    self.tracker.start()

    
    self.logger.info("Publisher '%s' created at '%s'" % (scope, address))
    
  def publish(self, obj):
    self.logger.debug("Publishing %s...", repr(obj))
    self.socket.send_string(self.scope, zmq.SNDMORE)
    self.socket.send_pyobj(obj)
    
  def get_subscriber_count(self):
    return self.tracker.subscribers
  
  def set_active(self, active):
    self.tracker.active = active
