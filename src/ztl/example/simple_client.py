#!/usr/bin/env python

import sys

from ztl.core.client import RemoteTask
from ztl.core.protocol import State

def main_cli():
  host = sys.argv[1]
  port = sys.argv[2]
  scope = sys.argv[3]
  payload = sys.argv[4]

  print("Connecting to host '%s:%s' at scope '%s'..." % (host, port, scope))
  task = RemoteTask(host, port, scope)
  print("Triggering task with payload '%s'..." % payload)
  mid, reply = task.trigger(payload)

  if mid > 0:
    print("Waiting 5s for task with ID '%s'..." % mid)
    state, reply = task.wait(mid, 5)
    if state < 0:
      print("Could not wait for task with ID '%s'. Payload is '%s'." % (mid, reply))
    elif state <= State.ACCEPTED:
      print("Aborting task with ID '%s'..." % mid)
      state, reply = task.abort(mid)
      if state == State.ABORTED:
        print("Task with ID '%s' aborted. Payload is '%s'." % (mid, reply))
      elif state <= State.ACCEPTED:
        print("Could not abort Task with ID '%s', waiting for completion. Payload is '%s'." % (mid, reply))
        task.wait(mid)
        print("Task with ID '%s' finished after unsuccessful abort signal. Payload is '%s'." % (mid, reply))
    else:
      print("Task with ID '%s' finished while waiting. Payload is '%s'." % (mid, reply))
  else:
    print("Task '%s' could not be triggered.")

if __name__ == "__main__":

  main_cli()
