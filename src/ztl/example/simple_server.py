#!/usr/bin/env python

import sys

from ztl.core.server import TaskServer
from ztl.core.protocol import State
from ztl.core.task import SimpleTaskHandler

def main_cli():
  scope = sys.argv[1]
  server = TaskServer(5555)
  server.register(scope, SimpleTaskHandler())
  server.listen()
  
if __name__ == "__main__":
  
  main_cli()
