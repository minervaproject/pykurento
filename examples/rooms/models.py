from examples import kurento
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker

from pykurento import media

engine = create_engine('sqlite:///rooms.db', echo=False)

Base = declarative_base(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

def get_session():
  return session

class Participant(Base):
  __tablename__ = "participants"

  id = Column(Integer, primary_key=True)
  incoming_endpoint_id = Column(String)
  room_id = Column(Integer, ForeignKey('rooms.id'))

  room = relationship("Room", backref=backref('participants', order_by=id))

  def get_incoming(self):
    if self.incoming_endpoint_id:
      incoming = media.WebRtcEndpoint(self.room.get_pipeline(), id=self.incoming_endpoint_id)
    else:
      incoming = media.WebRtcEndpoint(self.room.get_pipeline())
      self.incoming_endpoint_id = incoming.id
      session = get_session()
      session.add(self)
      session.commit()
    return incoming

  def get_answer(self, offer):
    return self.get_incoming().process_offer(offer)

  def connect(self, offer):
    incoming = self.get_incoming()
    outgoing = media.WebRtcEndpoint(self.room.get_pipeline())
    incoming.connect(outgoing)
    return outgoing.process_offer(offer)


class Room(Base):
  __tablename__ = "rooms"

  id = Column(Integer, primary_key=True)
  pipeline_id = Column(String)

  def get_pipeline(self):
    if self.pipeline_id:
      pipeline = kurento.get_pipeline(self.pipeline_id)
    else:
      pipeline = kurento.create_pipeline()
      self.pipeline_id = pipeline.id
      session = get_session()
      session.add(self)
      session.commit()

    return pipeline


Base.metadata.create_all(engine)