
import yaml

import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.client import RemoteTask

class Remotes():

  def __init__(self, configfile):

    self.logger = logging.getLogger('remote-config')
    self.remotes = {}
    self.config = {}

    with open(configfile) as f:
      self.config = yaml.safe_load(f)


  def get(self, name):

    if name in self.remotes:
      return self.remotes[name]

    else:
      rs = self.config["remotes"]
      if name in rs.keys():
        self.add(name, rs[name]["host"], rs[name]["port"], rs[name]["scope"])
        return self.remotes[name]

      return None


  def has(self, name):
    return name in self.remotes


  def add(self, name, host, port, scope):
    self.logger.info("Initialising remote task interface '%s'..." % name)
    self.remotes[name] = RemoteTask(host, port, scope)
