from pykurento import media
from pykurento.transport import KurentoTransport

class KurentoClient(object):
  def __init__(self, url):
    self.url = url
    self.transport = KurentoTransport(self.url)

  def get_transport(self):
    return self.transport

  def create_pipeline(self):
    return media.MediaPipeline(self)
