import websocket
import json
import time
import threading

class TimeoutError(Exception):
    pass

class Timeout:
  def __init__(self, seconds=1, error_message='Timeout'):
    self.seconds = seconds
    self.error_message = error_message
    self.timer = None

  def handle_timeout(self):
    raise TimeoutError(self.error_message)

  def __enter__(self):
    self.timer = threading.Timer(self.seconds, self.handle_timeout)
  
  def __exit__(self, type, value, traceback):
    if self.timer:
      self.timer.cancel()


class KurentoTransport:
  def __init__(self, url):
    self.url = url
    self.ws = websocket.WebSocket()
    self.current_id = 0
    self.session_id = None
    self.pending_operations = {}

    self.thread = threading.Thread(target=self._run_thread)
    self.thread.daemon = True
    self.thread.start()

  def _check_connection(self):
    if not self.ws.connected:
      print "Kurent Client websocket is not connected, reconnecting"
      with Timeout(seconds=5, error_message="Timeout: Kurento Client websocket connection timed out"):
        self.ws.connect(self.url)
        print "Kurent Client websocket connected!"

  def _run_thread(self):
    while True:
      try:
        self._check_connection()
        self.on_message(self.ws.recv())
        time.sleep(1)
      except Exception as ex:
        print "WS Receiver Thread Exception: %s" % str(ex)

  def next_id(self):
    self.current_id += 1
    return self.current_id

  def on_message(self, message):
    resp = json.loads(message)
    print "received message: %s" % message

    if 'error' in resp:
      raise Exception(resp['error']['message'])

    if 'result' in resp and 'sessionId' in resp['result']:
      self.session_id = resp['result']['sessionId']

    self.pending_operations["%d_response" % resp["id"]] = resp

  def rpc(self, rpc_type, **args):
    if self.session_id:
      args["sessionId"] = self.session_id

    request = {
      "jsonrpc": "2.0",
      "id": self.next_id(),
      "method": rpc_type,
      "params": args
    }
    req_key = "%d_request" % request["id"]
    resp_key = "%d_response" % request["id"]

    self.pending_operations[req_key] = request
    
    self._check_connection()

    print "sending message:  %s" % json.dumps(request)
    self.ws.send(json.dumps(request))

    while (resp_key not in self.pending_operations):
      time.sleep(1)

    resp = self.pending_operations[resp_key]
    
    del self.pending_operations[req_key]
    del self.pending_operations[resp_key]
        
    return resp['result']['value']

  def create(self, obj_type, **args):
    return self.rpc("create", type=obj_type, constructorParams=args)

  def invoke(self, object_id, operation, **args):
    return self.rpc("invoke", object=object_id, operation=operation, operationParams=args)

  def subscribe(self, object_id, event_type):
    return self.rpc("subscribe", object=object_id, type=event_type)

  def unsubscribe(self, subscription_id):
    return self.rpc("unsubscribe", subscription=subscription_id)

  def release(self, object_id):
    return self.rpc("release", object=object_id)

  def close(self):
    self.ws.close()
