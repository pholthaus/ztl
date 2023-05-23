#!/usr/bin/env python

import time
import yaml
import argparse
import os
import logging
logging.basicConfig(level=logging.INFO)

from sys import stdin, exit
from ztl.core.protocol import State, Task
from ztl.core.client import RemoteTask

class ScriptExecutor(object):

  tasks = {}

  def __init__(self, configfile, scriptfile):
    self.logger = logging.getLogger('script-exec')

    with open(configfile) as f:
      self.config = yaml.safe_load(f)

      rs = self.config["remotes"]
      for r in rs.keys():
        self.logger.info("Initialising remote task interface '%s'..." % r)
        self.tasks[r] = RemoteTask(rs[r]["host"], rs[r]["port"], rs[r]["scope"])

    with open(scriptfile) as f:
      self.script = yaml.safe_load(f)


  def execute_scene(self, scene):
    steps = sorted(list(self.script[scene].keys()))
    for step in steps:
      print("STARTING STEP '%s'" % step)

      task_ids = []
      handlers = self.script[scene][step].keys()
      for handler in handlers:
        if handler in self.tasks:
          components = self.script[scene][step][handler].keys()
          for component in components:
            goal = self.script[scene][step][handler][component]
            remote_id = self.tasks[handler].trigger(Task.encode(handler, component, goal))
            if remote_id > 0:
              task_ids.append(str(remote_id) + ":" + str(handler) + ":" + str(component) + ":" + str(goal))
            else:
              self.logger.error("Component '%s' on handler '%s' for step '%s' COULD NOT BE TRIGGERED." % (component, handler, step))
        else:
          self.logger.error("No remote for handler '%s'. Step '%s' COULD NOT BE TRIGGERED." % (handler, step))

      running = True
      while running:
        running = False
        for task_id in task_ids:
          components = task_id.split(":")
          remote_id = int(components[0])
          rid = components[1]
          status = self.client[rid].wait(remote_id, task_id, timeout=100)
          running = running or status <= State.ACCEPTED
        time.sleep(.1)


  def confirm_scene(self, scene):
    steps = list(self.script[scene].keys())

    for step in sorted(steps):
      print("STEP: %s" % step)
      handlers = self.script[scene][step].keys()
      for handler in handlers:
        components = self.script[scene][step][handler].keys()
        for component in components:
          goal = self.script[scene][step][handler][component]
          print("\t%s [%s]: -> %s" % (handler, component, goal))

    print("PRESS <ENTER> TO CONFIRM or ANY OTHER KEY TO SKIP")
    input = stdin.readline()
    return input == "\n"


  def execute(self):
    try:
        for scene in sorted(self.script.keys()):
          print("\n----------------------------")
          print("ABOUT TO EXECUTE SCENE '%s'" % scene)
          if self.confirm_scene(scene):
            print("EXECUTING SCENE '%s'" % scene)
            self.execute_scene(scene)
          else:
            print("\nSKIPPING SCENE '%s'" % (scene))

    except Exception as e:
      self.logger.error(e)
      exit(1)
    except KeyboardInterrupt:
      self.logger.error("Interrupted, exiting.")
      exit(1)

def main_cli():

  cfg_file = os.environ.get('XDG_CONFIG_HOME', os.environ.get('HOME', '/home/demo') + '/.config') + '/zmq-remotes.yaml'

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-c", "--config", type=str,
                      help="Configuration file location.", default=cfg_file)
  parser.add_argument("-s", "--script", type=str,
                      help="Script file to execute.", required=True)

  args, unknown = parser.parse_known_args()
  run = ScriptExecutor(args.config, args.script)
  run.execute()


if __name__ == "__main__":

  main_cli()

