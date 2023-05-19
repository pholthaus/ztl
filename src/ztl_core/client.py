import zmq
import time
import sys

from ztl_core.protocol import Message, Request, State

class ZMQClient(object):

  def __init__(self, host, port, scope, timeout=2000):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REQ)
    self.socket.setsockopt(zmq.RCVTIMEO, timeout)
    address = "tcp://" + str(host) + ":" + str(port)
    self.socket.connect(address)
    self.scope = scope

    print("ZMQ client sending to " + address)

  def trigger(self, payload):
    msg = Message.encode(self.scope, Request.INIT, -1, payload)
    try:
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["id"])
    except Exception as e:
      print("Exception: '%s' caught." % e)
      print(sys.exc_info()[0])
      print(sys.exc_info()[1])
      print(sys.exc_info()[2])
      return -1

  def abort(self, mid, payload="abort command"):
    try:
      msg = Message.encode(self.scope, Request.ABORT, mid, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["state"])
    except Exception as e:
      print("Exception: '%s' caught." % e)
      print(sys.exc_info()[0])
      print(sys.exc_info()[1])
      print(sys.exc_info()[2])
      return -1

  def status(self, mid, payload="status update"):
    try:
      msg = Message.encode(self.scope, Request.STATUS, mid, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["state"])
    except Exception as e:
      print("Exception: '%s' caught." % e)
      print(sys.exc_info()[0])
      print(sys.exc_info()[1])
      print(sys.exc_info()[2])
      return -1

  def wait(self, mid, timeout = 5.0):
    start = time.time()
    state = None
    while (time.time() - start) < timeout and mid > 0:
      state = self.status(mid)
      if not state == State.ACCEPTED:
        return state
      time.sleep(.1)
    return state
