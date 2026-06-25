import zmq
import logging
import cv2


logging.basicConfig(level=logging.INFO)

class ObjectPublisher(object):

  def __init__(self, port, scope):
    self.logger = logging.getLogger('object-publisher')
    context = zmq.Context()
    self.socket = context.socket(zmq.PUB)
    address = "tcp://*:" + str(port)
    self.socket.bind(address)
    self.scope = scope
    self.logger.info("Publisher '%s' established at '%s'" % (scope, address))
    
    
  def publish(self, obj):
    # self.logger.info("Publishing %s...", repr(obj))
    self.socket.send_string(self.scope, zmq.SNDMORE)
    self.socket.send_pyobj(obj)


def main_cli():
  p = ObjectPublisher(5555, "camera_frame")
  cap = cv2.VideoCapture(0)
  while True:
    p.publish(cap.read())
  

if __name__ == "__main__":

  main_cli()
