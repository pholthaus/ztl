#!/usr/bin/env python

import sys
import time

import argparse

from ztl.core.server import TaskServer
from ztl.core.protocol import State, Task
from ztl.core.task import ExecutableTask, TaskExecutor, TaskController


class PrintTask(ExecutableTask):

  def __init__(self, request):
    self.active = True
    self.request = request
    self.description = Task.decode(self.request)

  def execute(self):
    print("handler: " + self.description["handler"])
    print("component: " + self.description["component"])
    print("goal: " + self.description["goal"])
    time.sleep(3)
    return "finished"

  def abort(self):
    return False


class TaskTaskController(TaskController):

  def __init__(self):
    self.current_id = 0
    self.running = {}

  def init(self, request):
    self.current_id += 1
    print("Initialising Task ID '%s' (%s)..." % (self.current_id, request))
    self.running[self.current_id] = TaskExecutor(PrintTask, request)
    return self.current_id, "Initiated task '%s' with request: %s" % (self.current_id, request)

  def status(self, mid, request):
    if mid in self.running:
      state = self.running[mid].state()
      print("Status Task ID '%s' (%s): %s." % (mid, request, State.name(state)))
      if state < State.COMPLETED:
        return state, State.name(state)
      else:
        return state, self.running[mid].result()
    else:
      return State.REJECTED, "Invalid ID"

  def abort(self, mid, request):
    if mid in self.running:
      print("Aborting Task ID '%s' (%s)..." % (mid, request))
      success = self.running[mid].stop()
      state = self.running[mid].state()
      return state, success
    else:
      return State.REJECTED, "Invalid ID"

def main_cli():

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-p", "--port", type=int,
                      help="The port on the local machine that the server should listen to.", required=True)
  parser.add_argument("-s", "--scope", type=str,
                      help="The scope that the server should respond to.", required=True)

  args, unknown = parser.parse_known_args()

  server = TaskServer(args.port)
  server.register(args.scope, TaskTaskController())
  server.listen()


if __name__ == "__main__":

  main_cli()
