#!/usr/bin/env python

import sys

from ztl.core.client import RemoteTask
from ztl.core.protocol import State

def main_cli():
  host = sys.argv[1]
  scope = sys.argv[2]
  payload = sys.argv[3]

  print("Connecting to host '%s' at scope '%s'..." % (host, scope))
  run = RemoteTask(str(host), 5555, scope)
  print("Triggering task with payload '%s'..." % payload)
  mid = run.trigger(payload)
  print("Accepted as ID '%s'." % mid)
  state = run.wait(mid, 5)

  if state <= State.ACCEPTED:
    print("Aborting task with ID '%s'..." % mid)
    run.abort(mid)
    run.wait(mid)

  print("Task with ID '%s' finished." % mid)

if __name__ == "__main__":

  main_cli()
