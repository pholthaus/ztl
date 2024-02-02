#!/usr/bin/env python

import sys
import time

from ztl.core.server import TaskServer
from ztl.core.protocol import State, Task
from ztl.core.task import ExecutableTask, TaskExecutor, TaskController


class PrintTask(ExecutableTask):

  def __init__(self, request):
    self.active = True
    self.request = request

  def initialise(self):
    self.description = Task.decode(self.request)
    return True

  def execute(self):
    print("handler: " + self.description["handler"])
    print("component: " + self.description["component"])
    print("goal: " + self.description["goal"])
    return True

  def abort(self):
    return False, "Not running"


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
      print("Status Task ID '%s' (%s)..." % (mid, request))
      return self.running[mid].state(), State.name(self.running[mid].state())
    else:
      return State.REJECTED, "Invalid ID"


  def abort(self, mid, request):
    if mid in self.running:
      print("Aborting Task ID '%s' (%s)..." % (mid, request))
      return self.running[mid].stop()
    else:
      return State.REJECTED, "Invalid ID"


def main_cli():
  port = sys.argv[1]
  scope = sys.argv[2]
  server = TaskServer(port)
  server.register(scope, TaskTaskController())
  server.listen()


if __name__ == "__main__":

  main_cli()
