import tornado.web

from examples import kurento, render_view

class LoopbackHandler(tornado.web.RequestHandler):
  def on_event(self, *args, **kwargs):
    print "received event!"
    print args
    print kwargs

  def get(self):
    render_view(self, "loopback")

  def post(self):
    sdp_offer = self.request.body
    pipeline = kurento.create_pipeline()
    wrtc = media.WebRtcEndpoint(pipeline)

    wrtc.on_media_session_started_event(self.on_event)
    wrtc.on_media_session_terminated_event(self.on_event)

    sdp_answer = wrtc.process_offer(sdp_offer)
    self.finish(str(sdp_answer))

    # setup recording
    recorder = media.RecorderEndpoint(pipeline, uri="file:///tmp/test.webm")
    wrtc.connect(recorder)
    recorder.record()

    # plain old loopback
    # wrtc.connect(wrtc)

    # fun face overlay
    face = media.FaceOverlayFilter(pipeline)
    face.set_overlayed_image("https://raw.githubusercontent.com/minervaproject/pykurento/master/example/static/img/rainbowpox.png", 0, 0, 1, 1)
    wrtc.connect(face)
    face.connect(wrtc)

