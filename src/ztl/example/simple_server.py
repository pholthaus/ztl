#!/usr/bin/env python

import sys
import time

from ztl.core.server import TaskServer
from ztl.core.protocol import State
from ztl.core.task import ExecutableTask, TaskExecutor, TaskController


class DummyTask(ExecutableTask):

  def __init__(self, duration):
    self.active = True
    self.duration = duration

  def initialise(self):
    return True

  def execute(self):
    start = time.time()
    while self.active and time.time() - start < self.duration:
      time.sleep(.1)
    return self.active

  def abort(self):
    self.active = False
    return True


class SimpleTaskController(TaskController):

  def __init__(self):
    self.current_id = 0
    self.running = {}

  def init(self, payload):
    self.current_id += 1
    print("Initialising Task ID '%s' (%s)..." % (self.current_id, payload))
    self.running[self.current_id] = TaskExecutor(DummyTask, int(payload))
    return self.current_id, ""

  def status(self, mid, payload):
    if mid in self.running:
      print("Status Task ID '%s' (%s)..." % (mid, payload))
      return self.running[mid].state(), mid 
    else:
      return State.REJECTED, "Invalid ID"


  def abort(self, mid, payload):
    if mid in self.running:
      print("Aborting Task ID '%s' (%s)..." % (mid, payload))
      return self.running[mid].stop(), mid
    else:
      return State.REJECTED, "Invalid ID"


def main_cli():
  scope = sys.argv[1]
  server = TaskServer(5555)
  server.register(scope, SimpleTaskController())
  server.listen()


if __name__ == "__main__":

  main_cli()
