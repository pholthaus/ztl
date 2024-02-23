#!/usr/bin/env python

import sys

from ztl.core.client import RemoteTask
from ztl.core.protocol import State

def main_cli():
  host = sys.argv[1]
  port = sys.argv[2]
  scope = sys.argv[3]
  request = sys.argv[4]

  print("Connecting to host '%s:%s' at scope '%s'..." % (host, port, scope))
  task = RemoteTask(host, port, scope)
  print("Triggering task with request '%s'..." % request)
  mid, reply = task.trigger(request)

  if mid > 0:
    print("Initialised task with ID '%s'. Reply is '%s'." % (mid, reply))
    print("Waiting maximum 5s for the task to finish...")
    state, reply = task.wait(mid, 5)
    if state < 0:
      print("Could not wait for task with ID '%s'. Reply is '%s'." % (mid, reply))
    elif state <= State.ACCEPTED:
      print("Aborting task with ID '%s'..." % mid)
      state, reply = task.abort(mid)
      if state == State.ABORTED:
        print("Task with ID '%s' aborted. Reply is '%s'." % (mid, reply))
      elif state <= State.ACCEPTED:
        print("Could not abort Task with ID '%s', waiting for completion. Reply is '%s'." % (mid, reply))
        task.wait(mid)
        print("Task with ID '%s' finished after unsuccessful abort signal. Reply is '%s'." % (mid, reply))
    else:
      print("Task with ID '%s' finished while waiting. Result is '%s'." % (mid, reply))
  else:
    print("Task '%s' could not be triggered: '%s'." % reply)

if __name__ == "__main__":

  main_cli()
