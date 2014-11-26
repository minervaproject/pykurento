# This is the object graph as described at http://www.kurento.org/docs/5.0.3/mastering/kurento_API.html
#                   MediaObject
# Hub               MediaElement                MediaPipeline
#          HubPort    Endpoint    Filter
#           InputEndpoint OutputEndpoint

class MediaObject:
  MEDIA_PIPELINE = "MediaPipeline"

  # Endpoints
  HTTP_GET_ENDPOINT = "HttpGetEndpoint"
  HTTP_POST_ENDPOINT = "HttpPostEndpoint"
  PLAYER_ENDPOINT = "PlayerEndpoint"
  RECORDER_ENDPOINT = "RecorderEndpoint"
  RTP_ENDPOINT = "RtpEndpoint"
  WEB_RTC_ENDPOINT = "WebRtcEndpoint"

  # Filters
  Z_BAR_FILTER = "ZBarFilter"
  FACE_OVERLAY_FILTER = "FaceOverlayFilter"
  GSTREAMER_FILTER = "GStreamerFilter"

  # Hub
  COMPOSITE = "Composite"
  DISPATCHER = "Dispatcher"
  DISPATCHER_ONE_TO_MANY = "DispatcherOneToMany"

  def __init__(self, parent, id):
    self.parent = parent
    self.id = id

  def get_transport(self):
    return self.parent.get_transport()

  def get_pipeline(self):
    return self.parent.get_pipeline()

  def invoke(self, method, **args):
    return self.get_transport().invoke(self.id, method, **args)

  def release(self):
    return self.get_transport().release(self.id)


class MediaPipeline(MediaObject):
  def get_pipeline(self):
    return self

  def createWebRtcEndpoint(self):
    endpoint_id = self.get_transport().create(self.WEB_RTC_ENDPOINT, mediaPipeline=self.id)
    return WebRtcEndpoint(self, endpoint_id)


class MediaElement(MediaObject):
  CONNECT = "connect"

  def connect(self, sink):
    return self.invoke(self.CONNECT, sink=sink.id)


class WebRtcEndpoint(MediaElement):
  PROCESS_OFFER = "processOffer"

  def processOffer(self, offer):
    return self.invoke(self.PROCESS_OFFER, offer=offer)
