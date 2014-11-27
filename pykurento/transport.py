import websocket
import json
import time
import threading
import logging

logger = logging.getLogger(__name__)

class TimeoutException(Exception):
    pass


class Timeout(object):
  def __init__(self, seconds=1, error_message='Timeout'):
    self.seconds = seconds
    self.error_message = error_message
    self.timer = None

  def handle_timeout(self):
    raise TimeoutException(self.error_message)

  def __enter__(self):
    self.timer = threading.Timer(self.seconds, self.handle_timeout)
  
  def __exit__(self, type, value, traceback):
    if self.timer:
      self.timer.cancel()


class KurentoTransportException(Exception):
    def __init__(self, message, response={}):
      super(KurentoTransportException, self).__init__(message)
      self.response = response

    def __str__(self):
      return "%s - %s" % (str(self.message), json.dumps(self.response))


class KurentoTransport(object):
  def __init__(self, url):
    logger.debug("Creating new KurentoTransport with url: %s" % url)
    self.url = url
    self.ws = websocket.WebSocket()
    self.current_id = 0
    self.session_id = None
    self.pending_operations = {}
    self.subscriptions = {}
    self.stopped = False

    self.thread = threading.Thread(target=self._run_thread)
    self.thread.daemon = True
    self.thread.start()

  def __del__(self):
    logger.debug("Destroying KurentoTransport with url: %s" % self.url)
    self.stopped = True
    self.ws.close()

  def _check_connection(self):
    if not self.ws.connected:
      logger.info("Kurent Client websocket is not connected, reconnecting")
      try:
        with Timeout(seconds=5):
          self.ws.connect(self.url)
          logger.info("Kurent Client websocket connected!")
      except TimeoutException:
        # modifying this exception so we can differentiate in the receiver thread
        raise KurentoTransportException("Timeout: Kurento Client websocket connection timed out")

  def _run_thread(self):
    while not self.stopped:
      try:
        self._check_connection()
        with Timeout(seconds=1):
          self._on_message(self.ws.recv())
      except TimeoutException:
        logger.debug("WS Receiver Timeout")
      except Exception as ex:
        logger.error("WS Receiver Thread %s: %s" % (type(ex), str(ex)))

  def _next_id(self):
    self.current_id += 1
    return self.current_id

  def _on_message(self, message):
    resp = json.loads(message)
    logger.debug("received message: %s" % message)

    if 'method' in resp:
      if (resp['method'] == 'onEvent'
          and 'params' in resp
          and 'value' in resp['params']
          and 'subscription' in resp['params']
          and resp['params']['subscription'] in self.subscriptions):
        sub_id = resp['params']['subscription']
        fn = self.subscriptions[sub_id]
        self.session_id = resp['params']['sessionId'] if 'sessionId' in resp['params'] else self.session_id
        fn(resp["params"]["value"])

    else:
      if 'result' in resp and 'sessionId' in resp['result']:
        self.session_id = resp['result']['sessionId']
      self.pending_operations["%d_response" % resp["id"]] = resp

  def _rpc(self, rpc_type, **args):
    if self.session_id:
      args["sessionId"] = self.session_id

    request = {
      "jsonrpc": "2.0",
      "id": self._next_id(),
      "method": rpc_type,
      "params": args
    }
    req_key = "%d_request" % request["id"]
    resp_key = "%d_response" % request["id"]

    self.pending_operations[req_key] = request
    
    self._check_connection()

    logger.debug("sending message:  %s" % json.dumps(request))
    self.ws.send(json.dumps(request))

    while (resp_key not in self.pending_operations):
      time.sleep(1)

    resp = self.pending_operations[resp_key]
    
    del self.pending_operations[req_key]
    del self.pending_operations[resp_key]

    if 'error' in resp:
      raise KurentoTransportException(resp['error']['message'] if 'message' in resp['error'] else 'Unknown Error', resp)
    elif 'result' in resp and 'value' in resp['result']:
      return resp['result']['value']
    else:
      return None # just to be explicit

  def create(self, obj_type, **args):
    return self._rpc("create", type=obj_type, constructorParams=args)

  def invoke(self, object_id, operation, **args):
    return self._rpc("invoke", object=object_id, operation=operation, operationParams=args)

  def subscribe(self, object_id, event_type, fn):
    subscription_id = self._rpc("subscribe", object=object_id, type=event_type)
    self.subscriptions[subscription_id] = fn
    return subscription_id

  def unsubscribe(self, subscription_id):
    del self.subscriptions[subscription_id]
    return self._rpc("unsubscribe", subscription=subscription_id)

  def release(self, object_id):
    return self._rpc("release", object=object_id)
