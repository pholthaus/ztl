#!/usr/bin/env python3

import argparse
import time

import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.subscriber import ObjectSubscriber

    
class SimpleSubscriber(ObjectSubscriber):
  
  def callback(self, data):
    self.logger.info("Received data: %s..." % data)


def main_cli():
  
  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-r", "--remote", type=str,
                      help="The remote host to subscribe to.", required = True)
  parser.add_argument("-p", "--port", type=int,
                      help="The remote port to subscribe to.", required = True)
  parser.add_argument("-s", "--scope", type=str,
                      help="The scope where data is published under.", required = True)

  args, unknown = parser.parse_known_args()

  p = SimpleSubscriber(args.remote, args.port, args.scope)
  p.start()

if __name__ == "__main__":

  main_cli()
