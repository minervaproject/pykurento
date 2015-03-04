import tornado.web

from examples import kurento, render_view

class MultiResHandler(tornado.web.RequestHandler):
  low_res = None
  med_res = None
  high_res = None
  incoming = None

  def get(self):
    res = self.get_argument("res", None)
    if res and MultiResHandler.incoming:
      if res == "high":
        MultiResHandler.high_res.connect(MultiResHandler.incoming)
      elif res == "med":
        MultiResHandler.med_res.connect(MultiResHandler.incoming)
      elif res == "low":
        MultiResHandler.low_res.connect(MultiResHandler.incoming)
    else:
      render_view(self, "multires")

  def post(self):
    sdp_offer = self.request.body
    pipeline = kurento.create_pipeline()
    MultiResHandler.incoming = media.WebRtcEndpoint(pipeline)
    MultiResHandler.high_res = MultiResHandler.incoming
    MultiResHandler.low_res = media.GStreamerFilter(pipeline, command="capsfilter caps=video/x-raw,width=160,height=120", filterType="VIDEO")
    MultiResHandler.med_res = media.GStreamerFilter(pipeline, command="capsfilter caps=video/x-raw,width=320,height=240", filterType="VIDEO")

    sdp_answer = MultiResHandler.incoming.process_offer(sdp_offer)
    self.finish(str(sdp_answer))

    MultiResHandler.high_res.connect(MultiResHandler.incoming)
    MultiResHandler.incoming.connect(MultiResHandler.low_res)
    MultiResHandler.incoming.connect(MultiResHandler.med_res)
