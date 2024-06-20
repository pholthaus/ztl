#!/usr/bin/env python

import sys

from ztl.core.client import RemoteTask
from ztl.core.protocol import State, Task

def main_cli():
  host = sys.argv[1]
  port = sys.argv[2]
  scope = sys.argv[3]
  cmd = sys.argv[4].split(":")
  if len(sys.argv) > 5:
    timeout = int(sys.argv[5])
  else:
    timeout = 5

  print("Connecting to host '%s:%s' at scope '%s'..." % (host, port, scope))
  task = RemoteTask(host, port, scope)

  request = Task.encode(cmd[0], cmd[1], cmd[2])
  print("Triggering task with request '%s'..." % request)
  mid, reply = task.trigger(request)

  if mid > 0:
    print("Initialised task with ID '%s' for %ss. Reply is '%s'." % (mid, timeout, reply))
    state, reply = task.wait(mid, timeout=timeout)
    if state < 0:
      print("Could not wait for task with ID '%s'. Reply is '%s'." % (mid, reply))
    elif state <= State.ACCEPTED:
      print("Aborting task with ID '%s'..." % mid)
      state, reply = task.abort(mid)
      if state == State.ABORTED:
        print("Task with ID '%s' aborted. Reply is '%s'." % (mid, reply))
      elif state <= State.ACCEPTED:
        print("Could not abort Task with ID '%s', waiting for completion. Reply is '%s'." % (mid, reply))
        state, reply = task.wait(mid)
        print("Task with ID '%s' finished in state '%s' after unsuccessful abort signal. Reply is '%s'." % (mid, State.name(state), reply))
    else:
      print("Task with ID '%s' finished in state '%s' while waiting. Result is '%s'." % (mid, State.name(state), reply))

  else:
    print("Task '%s' could not be triggered: '%s'." % (mid, reply))

if __name__ == "__main__":

  main_cli()
