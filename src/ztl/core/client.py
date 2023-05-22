import zmq
import time
import sys
import logging

from ztl.core.protocol import Message, Request, State

class RemoteTask(object):

  def __init__(self, host, port, scope, timeout=2000):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REQ)
    self.socket.setsockopt(zmq.RCVTIMEO, timeout)
    address = "tcp://" + str(host) + ":" + str(port)
    self.socket.connect(address)
    self.scope = scope

    print("Remote task interface initialised at " + address)

  def trigger(self, payload):
    msg = Message.encode(self.scope, Request.INIT, -1, payload)
    try:
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["id"])
    except Exception as e:
      logging.error(e)
      return -1

  def abort(self, mid, payload="abort command"):
    try:
      msg = Message.encode(self.scope, Request.ABORT, mid, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["state"])
    except Exception as e:
      logging.error(e)
      return -1

  def status(self, mid, payload="status update"):
    try:
      msg = Message.encode(self.scope, Request.STATUS, mid, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["state"])
    except Exception as e:
      logging.error(e)
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
