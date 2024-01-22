#!/usr/bin/env python

import sys
import time

from ztl.core.server import TaskServer
from ztl.core.protocol import State, Task
from ztl.core.task import ExecutableTask, TaskExecutor, TaskController


class PrintTask(ExecutableTask):

  def __init__(self, payload):
    self.active = True
    self.payload = payload

  def initialise(self):
    self.description = Task.decode(self.payload)
    return True

  def execute(self):
    print("handler: " + self.description["handler"])
    print("component: " + self.description["component"])
    print("goal: " + self.description["goal"])
    return True

  def abort(self):
    return False


class TaskTaskController(TaskController):

  def __init__(self):
    self.current_id = 0
    self.running = {}

  def init(self, payload):
    self.current_id += 1
    print("Initialising Task ID '%s' (%s)..." % (self.current_id, payload))
    self.running[self.current_id] = TaskExecutor(PrintTask, payload)
    return self.current_id, payload

  def status(self, mid, payload):
    if mid in self.running:
      print("Status Task ID '%s' (%s)..." % (mid, payload))
      return self.running[mid].state(), payload
    else:
      return State.REJECTED, "Invalid ID"


  def abort(self, mid, payload):
    if mid in self.running:
      print("Aborting Task ID '%s' (%s)..." % (mid, payload))
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
