from gevent import monkey
monkey.patch_all()

from main import app
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

http_server = WSGIServer(('0.0.0.0', 5001), handler_class=WebSocketHandler)
if __name__ == '__main__':

    http_server.serve_forever()