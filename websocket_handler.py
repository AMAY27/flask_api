from gevent import monkey
monkey.patch_all()

from main import app
from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer

http_server = WSGIServer(('127.0.0.1', 5000), app, handler_class=WebSocketHandler)
if __name__ == '__main__':

    http_server.serve_forever()