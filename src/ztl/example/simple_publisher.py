import argparse
import time
import logging
logging.basicConfig(level=logging.INFO)

from ztl.core.publisher import ObjectPublisher

class SimplePublisher(ObjectPublisher):

  def run(self):
    self.logger = logging.getLogger('simple-pub')
    try:
      count = 0
      while True:
        data = {'one': 1, 'more': 2, 'count': count}
        self.logger.info("Publishing data: %s..." % data)
        self.publish(data)
        count = count + 1
        time.sleep(1)
    except Exception as e:
      self.logger.error("Exception while publishing: %s" % repr(e))


def main_cli():

  parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-p", "--port", type=int,
                      help="The port to listen listen on.", required = True)
  parser.add_argument("-s", "--scope", type=str,
                      help="The scope to publish data under.", required = True)

  args, unknown = parser.parse_known_args()

  publisher = SimplePublisher(args.port, args.scope)
  publisher.run()

if __name__ == "__main__":

  main_cli()

