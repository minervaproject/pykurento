import logging

logger = logging.getLogger(__name__)

# This is the object graph as described at http://www.kurento.org/docs/5.0.3/mastering/kurento_API.html
# We dont mimic it precisely yet as its still being built out, not all abstractions are necessary
#                   MediaObject
# Hub               MediaElement                MediaPipeline
#          HubPort    Endpoint    Filter


class MediaObject(object):
  def __init__(self, parent, **args):
    logger.debug("Creating new %s", self.__class__.__name__)
    self.parent = parent
    self.options = args
    self.id = self.get_transport().create(self.__class__.__name__, **args)

  def get_transport(self):
    return self.parent.get_transport()

  def get_pipeline(self):
    return self.parent.get_pipeline()

  def invoke(self, method, **args):
    return self.get_transport().invoke(self.id, method, **args)

  def subscribe(self, event, fn):
    def _callback(value):
      fn(value, self)
    return self.get_transport().subscribe(self.id, event, _callback)

  def release(self):
    return self.get_transport().release(self.id)


class MediaPipeline(MediaObject):
  def get_pipeline(self):
    return self


class MediaElement(MediaObject):
  def __init__(self, parent, **args):
    args["mediaPipeline"] = parent.get_pipeline().id
    super(MediaElement, self).__init__(parent, **args)

  def connect(self, sink):
    return self.invoke("connect", sink=sink.id)


# ENDPOINTS

class UriEndpoint(MediaElement):
  def get_uri(self):
    return self.invoke("getUri")

  def pause(self):
    return self.invoke("pause")

  def stop(self):
    return self.invoke("stop")


class PlayerEndpoint(UriEndpoint):
  def play(self):
    return self.invoke("play")

  def on_end_of_stream_event(self, fn):
    return self.subscribe("EndOfStream", fn)


class RecorderEndpoint(UriEndpoint):
  def record(self):
    return self.invoke("record")


class SessionEndpoint(MediaElement):
  def on_media_session_started_event(self, fn):
    return self.subscribe("MediaSessionStarted", fn)

  def on_media_session_terminated_event(self, fn):
    return self.subscribe("MediaSessionTerminated", fn)


class HttpEndpoint(SessionEndpoint):
  def get_url(self):
    return self.invoke("getUrl")


class HttpGetEndpoint(HttpEndpoint):
  pass


class HttpPostEndpoint(HttpEndpoint):
  def on_end_of_stream_event(self, fn):
    return self.subscribe("EndOfStream", fn)


class SdpEndpoint(SessionEndpoint):
  def generate_offer(self):
    return self.invoke("generateOffer")

  def process_offer(self, offer):
    return self.invoke("processOffer", offer=offer)

  def process_answer(self, answer):
    return self.invoke("processAnswer", answer=answer)

  def get_local_session_descriptor(self):
    return self.invoke("getLocalSessionDescriptor")

  def get_remote_session_descriptor(self):
    return self.invoke("getRemoteSessionDescriptor")


class RtpEndpoint(SdpEndpoint):
  pass

  
class WebRtcEndpoint(SdpEndpoint):
  pass


# FILTERS

class GStreamerFilter(MediaElement):
  pass


class FaceOverlayFilter(MediaElement):
  def set_overlayed_image(self, uri, offset_x, offset_y, width, height):
    return self.invoke("setOverlayedImage", uri=uri, offsetXPercent=offset_x, offsetYPercent=offset_y, widthPercent=width, heightPercent=height)


class ZBarFilter(MediaElement):
  def on_code_found_event(self, fn):
    return self.subscribe("CodeFound", fn)


# HUBS

class Composite(MediaElement):
  pass


class Dispatcher(MediaElement):
  pass


class DispatcherOneToMany(MediaElement):
  pass
