#!/usr/bin/env python

import uuid
import os
import sys
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
logging.getLogger().setLevel(logging.DEBUG)

import tornado.ioloop
import tornado.web

from pykurento import KurentoClient, media

kurento = KurentoClient("ws://localhost:8888/kurento")


class Participant(object):
  def __init__(self, room, offer):
    self.participant_id = str(uuid.uuid4())
    self.room = room
    self.offer = offer
    self.incoming = media.WebRtcEndpoint(self.room.pipeline)
    self.outgoings = {}
    self.answer = None

  def get_answer(self):
    if not self.answer:
      self.answer = self.incoming.process_offer(self.offer)

    return self.answer

  def connect(self, participant, offer):
    if participant.participant_id not in self.outgoings:
      self.outgoings[participant.participant_id] = media.WebRtcEndpoint(self.room.pipeline)
      self.incoming.connect(self.outgoings[participant.participant_id])

    outgoing = self.outgoings[participant.participant_id]
    return outgoing.process_offer(offer)


class Room(object):
  rooms = {}

  @classmethod
  def get(cls, room_id):
    if room_id not in cls.rooms:
      cls.rooms[room_id] = Room(room_id)
    return cls.rooms[room_id]

  def __init__(self, room_id):
    self.room_id = room_id
    self.participants = {}
    self.pipeline = kurento.create_pipeline()

  def add_participant(self, participant):
    self.participants[participant.participant_id] = participant
    return participant

  def get_participant(self, participant_id):
    return self.participants[participant_id] if participant_id in self.participants else None


class RoomHandler(tornado.web.RequestHandler):
  def get(self, room_id=None):
    room = Room.get(room_id)
    self.finish({"participants": [k for k in room.participants]})

  def post(self, room_id):
    room = Room.get(room_id)
    sdp_offer = self.request.body
    participant = room.add_participant(Participant(room, sdp_offer))
    sdp_answer = participant.get_answer()

    self.finish({
      "participant_id": participant.participant_id,
      "answer": sdp_answer
    })


class SubscribeToParticipantHandler(tornado.web.RequestHandler):
  def post(self, room_id, from_participant_id, to_participant_id):
    room = Room.get(room_id)
    sdp_offer = self.request.body
    from_participant = room.get_participant(from_participant_id)
    to_participant = room.get_participant(to_participant_id)

    if from_participant and to_participant:
      sdp_answer = from_participant.connect(to_participant, sdp_offer)
      self.finish({ "answer": sdp_answer })
      return
    else:
      self.set_status(409)
      self.finish({ "error": sdp_answer })
    

class IndexHandler(tornado.web.RequestHandler):
  def get(self):
    with open("index.html","r") as f:
      self.finish(f.read())


class RoomIndexHandler(tornado.web.RequestHandler):
  def get(self, room_id=None):
    with open("room.html","r") as f:
      self.finish(f.read())


class LoopbackHandler(tornado.web.RequestHandler):
  def get(self):
    with open("loopback.html","r") as f:
      self.finish(f.read())

  def post(self):
    sdp_offer = self.request.body
    pipeline = kurento.create_pipeline()
    wrtc_pub = media.WebRtcEndpoint(pipeline)
    sdp_answer = wrtc_pub.process_offer(sdp_offer)
    self.finish(str(sdp_answer))

    gst_flip = media.GStreamerFilter(pipeline, command="videoflip method=4")
    face_overlay = media.FaceOverlayFilter(pipeline)
    face_overlay.set_overlayed_image(
      "https://raw.githubusercontent.com/minervaproject/pykurento/master/example/static/img/rainbowpox.png", 
      0, 0, 1, 1)
    
    wrtc_pub.connect(gst_flip)
    gst_flip.connect(face_overlay)
    face_overlay.connect(wrtc_pub)


application = tornado.web.Application([
  (r"/", IndexHandler),
  (r"/loopback", LoopbackHandler),
  (r"/room", RoomIndexHandler),
  (r"/room/(?P<room_id>\d*)", RoomHandler),
  (r"/room/(?P<room_id>[^/]*)/subscribe/(?P<from_participant_id>[^/]*)/(?P<to_participant_id>[^/]*)", SubscribeToParticipantHandler),
  (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), "static")}),
], debug=True)

if __name__ == "__main__":
  application.listen(8080)
  print "Webserver now listening on port 8080"
  tornado.ioloop.IOLoop.instance().start()
  kurento.close()

