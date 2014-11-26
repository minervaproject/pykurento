# Pykurento

Pykurento is a [Kurento](http://www.kurento.org/docs/5.0.3/what_is_kurento.html) client written in python and uses the [websocket-client](https://github.com/liris/websocket-client) library for its transport layer.

## Installing

```
pip install git+https://github.com/minervaproject/pykurento.git#egg=pykurento
```

## Usage

Here's a simple example of a loopback pipeline created in a tornado request handler.

```python
from pykurento import KurentoClient

kurento = KurentoClient("ws://localhost:8888/kurento")

class LoopbackHandler(tornado.web.RequestHandler):
  def get(self):
    with open("loopback.html","r") as f:
      self.finish(f.read())

  def post(self):
    sdp_offer = self.request.body
    pipeline = kurento.createPipeline()
    wrtc_pub = pipeline.createWebRtcEndpoint()
    sdp_answer = wrtc_pub.processOffer(sdp_offer)
    wrtc_pub.connect(wrtc_pub)
    self.finish(str(sdp_answer))
```

[Source for loopback.html](https://github.com/minervaproject/pykurento/blob/master/example/loopback.html)


## Developing

### Source and deps

```
git clone https://github.com/minervaproject/pykurento
cd ./pykurento
pip install -r requirements.txt
```

### Running the example

```
cd ./example
./app.py
```

There are a couple of assumptions the example makes.
* You want to run on port 8080 - its hardcoded in there at the moment
* Your KMS address is localhost:8888 - again, hardcoded

For making the 2nd bullet work, the easiest way during development is to setup an ssh tunnel to your media server.

```
ssh -nNT -i <identity file> -L 8888:localhost:8888 <user>@<server address>
```

## License
As with Kurento, this client is released under the terms of [LGPL version 2.1](http://www.gnu.org/licenses/lgpl-2.1.html) license.

