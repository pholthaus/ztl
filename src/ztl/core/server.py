import zmq
import time
import sys
import logging

from ztl.core.protocol import Message, Request, State

class TaskServer(object):

  def __init__(self, port):
    context = zmq.Context()
    self.socket = context.socket(zmq.REP)
    address = "tcp://*:" + str(port)
    self.socket.bind(address)
    self.handlers = {}
    print("Task Server listening at '%s'" % address)


  def send_message(self, scope, mid, state, payload):
    self.socket.send(Message.encode(scope, mid, state, payload))


  def register(self, scope, handler):
    print("Registering handler for scope '%s'." % scope)
    self.handlers[scope] = handler


  def unregister(self, scope):
    self.handlers[scope] = None


  def listen(self):

    while True:
      try:
        message = self.socket.recv()
        request = Message.decode(message)

        if all(field in request for field in Message.FIELDS):

          scope = request["scope"]
          if scope in self.handlers:
            handler = self.handlers[scope]

            state = int(request["state"])
            mid = int(request["id"])
            payload = request["payload"]

            if state == Request.INIT:
              ticket, response = handler.init(payload)
              if ticket > 0:
                self.send_message(scope, State.ACCEPTED, ticket, response)
              else:
                self.send_message(scope, State.REJECTED, ticket, response)
            elif state == Request.STATUS:
              status, response = handler.status(mid, payload)
              self.send_message(scope, status, mid, response)
            elif state == Request.ABORT:
              status, response = handler.abort(mid, payload)
              self.send_message(scope, status, mid, response)
            else:
              self.send_message(scope, State.REJECTED, mid, "Invalid state")

          else:
            self.send_message(scope, State.REJECTED, -1, "No handler for scope: " + scope)
            print("No handler for scope '%s', ignoring." % scope)

        else:
          self.send_message(scope, State.REJECTED, -1, "Unknown protocol")
          print("Unknown command received '%s', ignoring." % message)

      except Exception as e:
        logging.error(e)
        time.sleep(1)
