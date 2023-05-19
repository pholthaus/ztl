#!/usr/bin/env python

import sys

from ztl_core.client import ZMQClient

if __name__ == "__main__":

  host = sys.argv[1]
  payload = sys.argv[2]

  run = ZMQClient(str(host), 5555, "/simple")
  print("Triggering task with payload '%s'..." % payload)
  mid = run.trigger(payload)
  print("Accepted as ID '%s'." % mid)
  run.wait(mid, 1)

  print("Aborting task with ID '%s'..." % mid)
  run.abort(mid)
  run.wait(mid)
  print("Task with ID '%s' finished." % mid)
