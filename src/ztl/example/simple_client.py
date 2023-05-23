#!/usr/bin/env python

import sys

from ztl.core.client import RemoteTask
from ztl.core.protocol import State

def main_cli():
  host = sys.argv[1]
  scope = sys.argv[2]
  payload = sys.argv[3]

  print("Connecting to host '%s' at scope '%s'..." % (host, scope))
  task = RemoteTask(str(host), 5555, scope)
  print("Triggering task with payload '%s'..." % payload)
  mid = task.trigger(payload)

  if mid > 0:
    print("Waiting 5s for task with ID '%s'..." % mid)
    state = task.wait(mid, 5)
    if state < 0:
      print("Could not wait for task with ID '%s'." % mid)
    elif state <= State.ACCEPTED:
      print("Aborting task with ID '%s'..." % mid)
      state = task.abort(mid)
      if state == State.ABORTED:
        print("Task with ID '%s' aborted." % mid)
      elif state <= State.ACCEPTED:
        print("Could not abort Task with ID '%s', waiting for completion." % mid)
        task.wait(mid)
        print("Task with ID '%s' finished after unsuccessful abort signal." % mid)
    else:
      print("Task with ID '%s' finished while waiting." % mid)
  else:
    print("Task '%s' could not be triggered.")

if __name__ == "__main__":

  main_cli()
