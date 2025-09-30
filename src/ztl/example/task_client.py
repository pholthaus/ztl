#!/usr/bin/env python

import sys

import argparse

from ztl.core.client import RemoteTask
from ztl.core.protocol import State, Task

def main_cli():

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-r", "--remote", type=str,
                      help="The remote hostname or IP of the server to execute the task.", required=True)
  parser.add_argument("-p", "--port", type=int,
                      help="The port on the remote host that should execute the task.", required=True)
  parser.add_argument("-s", "--scope", type=str,
                      help="The scope that the server is listening to.", required=True)
  parser.add_argument("-t", "--timeout", type=int,
                      help="An optional timeout to wait for task completion, continues waiting if 0 or less", required=False, default=-1)
  parser.add_argument("payload", type=str,
                      help="The task specification payload, with handler, component and goal separated by ':', e.g. 'handler:component:goal'.")


  args, unknown = parser.parse_known_args()
  cmd = args.payload.split(":", 2)
  if len(cmd) < 3:
    print("Error: Invalid task specification. Payload needs to specify handler, component and goal separated by ':', e.g. 'handler:component:goal'")
    parser.print_help(sys.stderr)
    return -1

  print("Connecting to host '%s:%s' at scope '%s'..." % (args.remote, args.port, args.scope))
  task = RemoteTask(args.remote, args.port, args.scope)

  request = Task.encode(cmd[0], cmd[1], cmd[2])

  print("Triggering task with request '%s'..." % request)
  mid, reply = task.trigger(request)

  if mid > 0:
    print("Initialised task with ID '%s' for %ss. Reply is '%s'." % (mid, args.timeout, reply))
    state, reply = task.wait(mid, timeout=args.timeout)
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
