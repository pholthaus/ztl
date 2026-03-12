
import yaml

import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.client import RemoteTask

class Remotes():

  def __init__(self, configfile):

    self.logger = logging.getLogger('remote-config')
    self.remotes = {}

    with open(configfile) as f:
      config = yaml.safe_load(f)
      rs = config["remotes"]
      for name in rs.keys():
        self.add(name, rs[name]["host"], rs[name]["port"], rs[name]["scope"])


  def get(self, name):
    return self.remotes[name]


  def has(self, name):
    return name in self.remotes


  def add(self, name, host, port, scope):
    self.logger.info("Initialising remote task interface '%s'..." % name)
    self.remotes[name] = RemoteTask(host, port, scope)
