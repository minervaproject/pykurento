# Pykurento

[![Join the chat at https://gitter.im/minervaproject/pykurento](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/minervaproject/pykurento?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

Pykurento is a [Kurento](http://www.kurento.org/docs/5.0.3/what_is_kurento.html) client written in python and uses the [websocket-client](https://github.com/liris/websocket-client) library for its transport layer.

## Installing

```
pip install git+https://github.com/minervaproject/pykurento.git#egg=pykurento
```

## Usage

Here's a simple example of a loopback pipeline created in a tornado request handler.

```python
from pykurento import KurentoClient, media

kurento = KurentoClient("ws://localhost:8888/kurento")

class LoopbackHandler(tornado.web.RequestHandler):
  def get(self):
    with open("loopback.html","r") as f:
      self.finish(f.read())

  def post(self):
    sdp_offer = self.request.body
    pipeline = kurento.create_pipeline()
    wrtc_pub = media.WebRtcEndpoint()
    sdp_answer = wrtc_pub.process_offer(sdp_offer)
    wrtc_pub.connect(wrtc_pub)
    self.finish(str(sdp_answer))
```

[Source for loopback.html](https://github.com/minervaproject/pykurento/blob/master/examples/views/loopback.html)


## Developing

### Source and deps

```
git clone https://github.com/minervaproject/pykurento
cd ./pykurento
pip install -r examples/requirements.txt
```

### Running the examples

```
./examples/app.py
```

or

```
PORT=8080 ./examples/app.py
```

There is an assumption in the examples that your KMS address is localhost:8888. The easiest way during development to make this work is to setup an ssh tunnel to your media server.

```
ssh -nNT -i <identity file> -L 8888:localhost:8888 <user>@<server address>
```

### Gitter Chatroom
Find out more info in the Gitter chatroom, located at https://gitter.im/minervaproject/pykurento

## License
As with Kurento, this client is released under the terms of [LGPL version 2.1](http://www.gnu.org/licenses/lgpl-2.1.html) license.

