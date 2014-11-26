from pykurento import media
from pykurento.transport import KurentoTransport

class KurentoClient:
  def __init__(self, url):
    self.url = url
    self.transport = KurentoTransport(self.url)

  def get_transport(self):
    return self.transport

  def createPipeline(self):
    pipeline_id = self.transport.create(media.MediaObject.MEDIA_PIPELINE)
    return media.MediaPipeline(self, pipeline_id)

  def close(self):
    self.transport.close()
