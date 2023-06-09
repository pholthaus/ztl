import zmq
import time
import sys
import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.protocol import Message, Request, State

class TaskServer(object):

  def __init__(self, port):
    self.logger = logging.getLogger('remote-task')
    context = zmq.Context()
    self.socket = context.socket(zmq.REP)
    address = "tcp://*:" + str(port)
    self.socket.bind(address)
    self.handlers = {}
    self.logger.info("Task Server listening at '%s'" % address)


  def send_message(self, scope, mid, state, payload):
    self.socket.send(Message.encode(scope, mid, state, payload))


  def register(self, scope, handler):
    """
    Register a new handler for requests on a specific scope.

    Parameters
    ----------
    scope: The scope for which the server should dispatch tasks to the handler. Will replace any existing handler for this scope.
    handler: A handler object that will be called with requests (init, status, abort)
    """

    self.logger.info("Registering handler for scope '%s'." % scope)
    self.handlers[scope] = handler


  def unregister(self, scope):
    """
    Unregister any handler on a given scope.

    Parameters
    ----------
    scope: The scope for which the server should not dispatch tasks any longer.
    """
    self.handlers[scope] = None
    self.logger.info("Handler for scope '%s' removed." % scope)


  def listen(self):
    """
    Begin listening to requests and dispatching them to any handlers if available. This method blocks until interrupted.

    """
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

            try:
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
                self.send_message(scope, State.REJECTED, mid, "Invalid request")
            except Exception as e:
              logging.error(e)
              self.send_message(scope, State.FAILED, mid, "Handler threw exception: " + str(e))
          else:
            self.send_message(scope, State.REJECTED, -1, "No handler for scope: " + scope)
            self.logger.warning("No handler for scope '%s', ignoring." % scope)

        else:
          self.send_message(scope, State.REJECTED, -1, "Unknown protocol")
          self.logger.warning("Unknown command received '%s', ignoring." % message)

      except Exception as e:
        logging.error(e)
        time.sleep(1)
      except KeyboardInterrupt:
        logging.error("Interrupted, exiting.")
        sys.exit(1)
