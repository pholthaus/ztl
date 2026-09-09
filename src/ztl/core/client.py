import zmq
import time
import sys
import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.protocol import Message, Request, State

class RemoteTask(object):

  def __init__(self, host, port, scope, timeout=2000):

    self.logger = logging.getLogger('remote-task')
    self.context = zmq.Context()
    self.address = "tcp://" + str(host) + ":" + str(port)
    self.timeout = timeout
    self.scope = scope
    self.socket = None
    self._connect()

    self.logger.info("Remote task interface initialised at '%s'.", self.address)

  def _connect(self):
    if self.socket is not None:
      self.logger.warning("Reconnecting remote task interface at '%s'.", self.address)
      self.socket.setsockopt(zmq.LINGER, 0)
      self.socket.close()

    self.socket = self.context.socket(zmq.REQ)
    self.socket.setsockopt(zmq.RCVTIMEO, self.timeout)
    self.socket.setsockopt(zmq.SNDTIMEO, self.timeout)
    self.socket.setsockopt(zmq.LINGER, 1)

    self.socket.connect(self.address)

  def _disconnect(self):
    if not self.socket is None:
      self.socket.setsockopt(zmq.LINGER, 0)
      self.socket.close()
      self.socket = None


  def trigger(self, payload):
    """
    Trigger a task at the remote interface.

    Parameters
    ----------
    payload: The payload containing the task description.

    Returns
    -------
    id: An ID for the task assigned by the server if accepted, -1 if rejected or server not reachable or communication error.
    reply: The remote reply containing an updated task description or the error message if rejected or server not reachable or communication error.
    """
    try:
      if self.socket is None:
        self._connect()
      msg = Message.encode(self.scope, Request.INIT, -1, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["id"]), reply["payload"]
    except zmq.error.ZMQError as e:
      self._disconnect()
      self.logger.error("Networking error, disconnecting: %s", repr(e))
      return -1, repr(e)
    except Exception as e:
      self.logger.error("Exception occurred: %s", repr(e))
      return -1, repr(e)

  def abort(self, mid, payload="abort command"):
    """
    Aborts a task at the remote interface.

    Parameters
    ----------
    mid: The ID of the task to abort.
    payload: An optional payload containing an updated task description. Default: "abort command"

    Returns
    -------
    status: The updated status after attempting to abort. Task might not be aborted. -1 if server not reachable or communication error.
    reply: The remote reply containing an updated task description. May contain error message if task not aborted or server not reachable or communication error.
    """
    try:
      if self.socket is None:
        self._connect()
      msg = Message.encode(self.scope, Request.ABORT, mid, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["state"]), reply["payload"]
    except zmq.error.ZMQError as e:
      self._disconnect()
      self.logger.error("Networking error, disconnecting: %s", repr(e))
      return -1, repr(e)
    except Exception as e:
      self.logger.error("Exception occurred: %s", repr(e))
      return -1, repr(e)

  def status(self, mid, payload="status update"):
    """
    Query the status of a given task at the remote interface.

    Parameters
    ----------
    mid: The ID of the task to query about.
    payload: An optional payload containing an updated task description. Default: "status update"

    Returns
    -------
    status: The current status of the task at the server. State.FAILED if server not reachable or communication error.
    reply: The remote reply containing an updated task description or the error message if server not reachable or communication error.
    """
    try:
      if self.socket is None:
        self._connect()
      msg = Message.encode(self.scope, Request.STATUS, mid, payload)
      self.socket.send(msg)
      reply = Message.decode(self.socket.recv())
      return int(reply["state"]), reply["payload"]
    except zmq.error.ZMQError as e:
      self._disconnect()
      self.logger.error("Networking error, disconnecting: %s", repr(e))
      return State.FAILED, repr(e)
    except Exception as e:
      self.logger.error("Exception occurred: %s", repr(e))
      return State.FAILED, repr(e)

  def wait(self, mid, payload = "waiting poll", timeout = 5.0):
    """
    Wait for a task to complete at the remote interface.

    Parameters
    ----------
    mid: The ID of the task to wait for.
    payload: An optional payload containing an updated task description. Default: "waiting poll"
    timeout: Maximum time to wait, interpreted as infinite when equal or smaller than 0. Default: 5.0 secs.

    Returns
    -------
    state: The last task status after waiting complete. State.FAILED if server not reachable or communication error.
    reply: The remote reply containing an updated task description or the error message if server not reachable or communication error.
    """
    start = time.time()
    state = -1
    reply = None
    while timeout <= 0 or (time.time() - start) < timeout:
      state, reply = self.status(mid, payload = payload)
      if state > State.ACCEPTED:
        return state, reply
      time.sleep(.1)
    return state, reply
