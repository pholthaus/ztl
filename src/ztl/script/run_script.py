#!/usr/bin/env python

import time
import oyaml as yaml
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

  def parse_stage(self, stage):
    name = stage
    delay = 0
    wait = True
    o = stage.find("(")
    c = stage.find(")")
    if o > 0 and c > 0:
      params = stage[o+1:c]
      name = stage[0:o]
      for param in params.split(","):
        pp = param.split("=")
        if len(pp) is 2:
          key = pp[0].strip()
          value = pp[1].strip()
          if key == "delay":
            delay = int(value)
          if key == "wait":
            wait = value.lower() in ['true', '1', 't', 'y', 'yes']
    return name, delay, wait

  def execute_scene(self, scene):

    scene_name, scene_delay, scene_wait = self.parse_stage(scene)
    steps = list(self.script[scene].keys())

    print(("EXECUTING SCENE '%s'" % scene_name) + (" WITH DELAY %ss" % scene_delay if scene_delay > 0 else "") + "...")

    if scene_delay > 0:
      time.sleep(scene_delay)

    for step in steps:
      step_name, step_delay, step_wait = self.parse_stage(step)
      print(("STARTING STEP '%s'" % step_name) + (" IN BACKGROUND" if not step_wait else "") + (" WITH DELAY %ss" % step_delay if step_delay > 0 else "") + "...")

      if step_delay > 0:
        time.sleep(step_delay)

      task_ids = []
      handlers = self.script[scene][step].keys()
      for handler in handlers:
        if handler in self.tasks:
          components = self.script[scene][step][handler].keys()
          for component in components:
            goal = self.script[scene][step][handler][component]
            remote_id = self.tasks[handler].trigger(Task.encode(handler, component, goal))
            if remote_id > 0:
              if step_wait:
                task_ids.append(str(remote_id) + ":" + str(handler) + ":" + str(component) + ":" + str(goal))
              else:
                # MOVE TO DEBUG AFTER FINISHING THIS FEATURE
                self.logger.info("Component '%s' on handler '%s' for step '%s' TRIGGERED TO RUN IN BACKGROUND." % (component, handler, step_name))
            else:
              self.logger.error("Component '%s' on handler '%s' for step '%s' COULD NOT BE TRIGGERED." % (component, handler, step_name))
        else:
          self.logger.error("No remote for handler '%s'. Step '%s' COULD NOT BE TRIGGERED." % (handler, step_name))

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
    print("\n----------------------------")
    print("ABOUT TO EXECUTE SCENE '%s'" % scene)

    steps = list(self.script[scene].keys())

    for step in steps:
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
        for scene in self.script.keys():
          if self.confirm_scene(scene):
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

