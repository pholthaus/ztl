#!/usr/bin/env python

import sys

from ztl_core.server import ZMQServer
from ztl_core.protocol import State

class ZMQSimpleHandler(object):

  current_id = 0
  running = {}


  def init(self, payload):
    self.current_id += 1
    print("Initialising Task ID '%s' (%s)..." % (self.current_id, payload))
    self.running[self.current_id] = State.ACCEPTED
    return self.current_id, ""


  def status(self, mid, payload):
    if mid in self.running:
      print("Status Task ID '%s' (%s)..." % (mid, payload))
      return self.running[mid], mid
    else:
      return State.REJECTED, "Invalid ID"


  def abort(self, mid, payload):
    if mid in self.running:
      print("Aborting Task ID '%s' (%s)..." % (mid, payload))
      self.running[mid] = State.ABORTED
      return self.running[mid], mid
    else:
      return State.REJECTED, "Invalid ID"


if __name__ == "__main__":
  run = ZMQServer(5555)
  run.register("/simple", ZMQSimpleHandler())
  run.execute()
