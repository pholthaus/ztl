import argparse
import os

import oyaml as yaml

import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.client import RemoteTask
from ztl.core.subscriber import ObjectSubscriber

class ZMQEndpoints():

  def __init__(self, parser = None):

    self.logger = logging.getLogger('remote-config')
    self.remotes = {}
    self.publishers = {}
    self.config = {}

    if parser is None:
      parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--config",
                        type=str,
                        help="Configuration file location.",
                        default=os.environ.get(
                          'XDG_CONFIG_HOME', os.environ.get('HOME', '/home/demo') + '/.config')
                        + '/zmq-remotes.yaml')
    parser.add_argument('--publisher',
                        action='append',
                        nargs=4,
                        metavar=("NAME", "HOST", "PORT", "SCOPE"),
                        help="add or override publisher configuration identified by NAME listening at HOST:PORT under SCOPE")
    parser.add_argument('--task',
                        action='append',
                        nargs=4,
                        metavar=("NAME", "HOST", "PORT", "SCOPE"),
                        help="add or override remote task configuration identified by NAME listening at HOST:PORT under SCOPE")

    args, unknown = parser.parse_known_args()

    with open(args.config) as f:
      self.config = yaml.safe_load(f)

    if args.task:
      for remote in args.task:
        self.config["remotes"][remote[0]] = {"host": remote[1],
                                    "port": int(remote[2]),
                                    "scope": remote[3]}

    if args.publisher:
      for remote in args.publisher:
        self.config["publishers"][remote[0]] = {"host": remote[1],
                                    "port": int(remote[2]),
                                    "scope": remote[3]}


  def get_remote(self, name):
    if name in self.remotes:
      return self.remotes[name]

    else:
      rs = self.config["remotes"]
      if name in rs.keys():
        self.add_remote(name, rs[name]["host"], rs[name]["port"], rs[name]["scope"])
        return self.remotes[name]

      return None


  def add_remote(self, name, host, port, scope):
    self.logger.info("Initialising remote task interface '%s'..." % name)
    if name in self.remotes:
      self.logger.warning("Overriding existing remote task interface '%s'." % name)
    self.remotes[name] = RemoteTask(host, port, scope)


  def has_remote(self, name):
    return name in self.remotes or name in self.config["remotes"]


  def get_remote_config(self, name):
    return self.config["remotes"][name]


  def get_subscriber(self, name):
    if name in self.publishers:
      return self.publishers[name]

    else:
      ps = self.config["publishers"]
      if name in ps.keys():
        self.add_subscriber(name, ps[name]["host"], ps[name]["port"], ps[name]["scope"])
        return self.publishers[name]

      return None


  def add_subscriber(self, name, host, port, scope):
    self.logger.info("Initialising subscriber for publisher '%s'..." % name)
    if name in self.publishers:
      self.logger.warning("Overriding existing subscriber for publisher '%s'." % name)
    self.publishers[name] = ObjectSubscriber(host, port, scope)


  def has_publisher(self, name):
    return name in self.publishers or name in self.config["publishers"]


  def get_publisher_config(self, name):
    return self.config["publishers"][name]
