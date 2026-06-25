import zmq
import logging

logging.basicConfig(level=logging.INFO)

class ObjectSubscriber(object):
  
  def __init__(self, host, port, scope):
    self.logger = logging.getLogger('object-subscriber')
    context = zmq.Context()
    self.socket = context.socket(zmq.SUB)
    address = "tcp://" + str(host) + ":" + str(port)
    self.socket.connect(address)
    self.socket.setsockopt_string(zmq.SUBSCRIBE, scope)
    self.logger.info("Subscriber '%s' established at '%s'" % (scope, address))

    
  def listen(self):
    self.logger.info("Start listening...")
    while True:
        topic = self.socket.recv_string()
        obj = self.socket.recv_pyobj()
        print(obj)

def main_cli():
  p = ObjectSubscriber("localhost", 5555, "camera_frame")
  p.listen()

if __name__ == "__main__":

  main_cli()
