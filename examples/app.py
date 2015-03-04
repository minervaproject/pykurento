#!/usr/bin/env python

import os
import sys
import logging
import signal
import tornado.ioloop
import tornado.web


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logging.getLogger().setLevel(logging.DEBUG)

from examples import render_view
import examples.loopback.handlers
import examples.rooms.handlers
import examples.multires.handlers


class IndexHandler(tornado.web.RequestHandler):
  def get(self):
    render_view(self, "index")

application = tornado.web.Application([
  (r"/", IndexHandler),
  (r"/loopback", examples.loopback.handlers.LoopbackHandler),
  (r"/multires", examples.multires.handlers.MultiResHandler),
  (r"/room", examples.rooms.handlers.RoomIndexHandler),
  (r"/room/(?P<room_id>\d*)", examples.rooms.handlers.RoomHandler),
  (r"/room/(?P<room_id>[^/]*)/subscribe/(?P<from_participant_id>[^/]*)/(?P<to_participant_id>[^/]*)", examples.rooms.handlers.SubscribeToParticipantHandler),
  (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
], debug=True)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 8080))
  application.listen(port)
  print "Webserver now listening on port %d" % port
  ioloop = tornado.ioloop.IOLoop.instance()
  signal.signal(signal.SIGINT, lambda sig, frame: ioloop.stop())
  ioloop.start()
