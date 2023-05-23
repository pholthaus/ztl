import base64

class Request:

  INIT = 1
  STATUS = 2
  ABORT = 3

  @staticmethod
  def name(code):
    if code == Request.INIT: return "INIT"
    if code == Request.STATUS: return "STATUS"
    if code == Request.ABORT: return "ABORT"
    return None

class State:

  INITIATED = 0
  ACCEPTED = 1
  REJECTED = 2
  FAILED = 3
  ABORTED = 4
  COMPLETED = 5

  @staticmethod
  def name(code):
    if code == State.INITIATED: return "INITIATED"
    if code == State.ACCEPTED: return "ACCEPTED"
    if code == State.REJECTED: return "REJECTED"
    if code == State.FAILED: return "FAILED"
    if code == State.ABORTED: return "ABORTED"
    if code == State.COMPLETED: return "COMPLETED"
    return None

class Message:

  SEPARATOR = ";"
  FIELDS = ["scope", "state", "id", "payload"]

  @staticmethod
  def encode(scope, state, mid, payload):
    msg = {"scope": str(scope),
           "state": str(state),
           "id": str(mid),
           "payload": str(payload)}
    return (msg["scope"] + Message.SEPARATOR  + msg["state"] + Message.SEPARATOR + msg["id"] + Message.SEPARATOR + msg["payload"]).encode('utf-8')

  @staticmethod
  def decode(message):
    split = message.decode("utf-8").split(Message.SEPARATOR)
    unfolded = dict(zip(Message.FIELDS, split))
    return unfolded


class Task:

  SEPARATOR = "^"
  FIELDS = ["handler", "component", "goal"]

  @staticmethod
  def decode(message):
    cmd = base64.b64decode(bytes(str(message).encode("utf-8"))).split(Task.SEPARATOR)
    return dict(zip(Task.FIELDS, cmd))

  @staticmethod
  def encode(handler, component, goal):
    joined = str(handler) + Task.SEPARATOR + str(component) + Task.SEPARATOR + str(goal)
    code = base64.b64encode(joined.encode('utf-8'))
    return code.decode("utf-8")
