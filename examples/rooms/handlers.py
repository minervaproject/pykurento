import tornado.web
from examples import render_view
from examples.rooms import models

session = models.get_session()

class RoomIndexHandler(tornado.web.RequestHandler):
  def get(self):
    render_view(self, "room")


class RoomHandler(tornado.web.RequestHandler):
  def get(self, room_id=None):
    room = session.query(models.Room).get(room_id)
    if room:
      self.finish({"participants": [p.id for p in room.participants]})
    else:
      self.finish({"error": "missing room"})

  def post(self, room_id):
    room = session.query(models.Room).get(room_id)
    if not room:
      room = models.Room(id=room_id)
      session.add(room)
      session.commit()

    sdp_offer = self.request.body
    
    participant = models.Participant(room_id=room_id)
    session.add(participant)
    session.commit()
    
    sdp_answer = participant.get_answer(sdp_offer)

    self.finish({
      "participant_id": participant.id,
      "answer": sdp_answer
    })


class SubscribeToParticipantHandler(tornado.web.RequestHandler):
  def post(self, room_id, from_participant_id, to_participant_id):
    sdp_offer = self.request.body
    from_participant = session.query(models.Participant).get(from_participant_id)
    to_participant = session.query(models.Participant).get(to_participant_id)

    if from_participant and to_participant:
      sdp_answer = from_participant.connect(sdp_offer)
      self.finish({ "answer": sdp_answer })
    else:
      self.set_status(409)
      self.finish({ "error": "participants matching ids not found" })
    