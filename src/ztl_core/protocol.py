import base64

class Request:

  INIT = 1
  STATUS = 2
  ABORT = 3


class State:

  REJECTED = 1
  ACCEPTED = 2
  FAILED = 3
  ABORTED = 4
  COMPLETED = 5


class Message:

  SEPARATOR = ";"
  FIELDS = ["scope", "state", "id", "payload"]

  def encode(scope, state, mid, payload):
    msg = {"scope": str(scope),
           "state": str(state),
           "id": str(mid),
           "payload": str(payload)}
    return (msg["scope"] + Message.SEPARATOR  + msg["state"] + Message.SEPARATOR + msg["id"] + Message.SEPARATOR + msg["payload"]).encode('utf-8')

  def decode(message):
    split = message.decode("utf-8").split(Message.SEPARATOR)
    unfolded = dict(zip(Message.FIELDS, split))
    return unfolded


class Task:

  SEPARATOR = "^"
  FIELDS = ["handler", "component", "goal"]

  def decode(self, message):
    cmd = base64.b64decode(bytes(message)).split(self.SEPARATOR)
    return dict(zip(self.FIELDS, cmd))

  def encode(self, handler, component, goal):
    joined = str(handler) + self.SEPARATOR + str(component) + self.SEPARATOR + str(goal)
    code = base64.b64encode(joined.encode('utf-8'))
    return code.decode("utf-8")
