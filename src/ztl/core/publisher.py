import zmq
import logging

logging.basicConfig(level=logging.INFO)

class ObjectPublisher(object):

  def __init__(self, port, scope):
    self.logger = logging.getLogger('object-publisher')
    context = zmq.Context()
    self.socket = context.socket(zmq.PUB)
    address = "tcp://*:" + str(port)
    self.socket.bind(address)
    self.scope = scope
    self.logger.info("Publisher '%s' created at '%s'" % (scope, address))
    
  def publish(self, obj):
    self.logger.debug("Publishing %s...", repr(obj))
    self.socket.send_string(self.scope, zmq.SNDMORE)
    self.socket.send_pyobj(obj)  
