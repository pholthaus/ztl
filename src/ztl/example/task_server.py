#!/usr/bin/env python

import sys
import time

import argparse

from ztl.core.server import TaskServer
from ztl.core.protocol import State, Task
from ztl.core.task import ExecutableTask, TaskExecutor, TaskController


class TestTask(ExecutableTask):

  def __init__(self, component, goal):
    self.active = True
    self.component = component
    self.goal = goal

  def execute(self):
    if self.component == "echo":
      return self.goal
    if self.component == "print":
      print("component: " + self.component)
      print("goal: " + self.goal)
      return True
    if self.component == "sleep":
      time.sleep(int(self.goal))
      return True
    else:
      raise RuntimeError("No such component '%s', try 'echo/print/sleep'." % self.component)

  def abort(self):
    return False


class TestController(TaskController):

  def assign(self, handler, component, goal):
    if handler == "test":
      return TestTask, component, goal
    raise RuntimeError("No such handler '%s', try 'test'." % handler)


def main_cli():

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-p", "--port", type=int,
                      help="The port on the local machine that the server should listen to.", required=True)
  parser.add_argument("-s", "--scope", type=str,
                      help="The scope that the server should respond to.", required=True)

  args, unknown = parser.parse_known_args()

  server = TaskServer(args.port)
  server.register(args.scope, TestController())
  server.listen()


if __name__ == "__main__":

  main_cli()
