# main.py
import eventlet
eventlet.monkey_patch()

import logging
import numpy as np
from flask import Flask
from flask_socketio import SocketIO
from io import BytesIO

# replace these imports with wherever your model code lives
from model.modelanalyselive import get_model, list_of_models, run_audio 


SR = 44100              # sampling rate
WINDOW_SEC = 4          # how many seconds to buffer
WINDOW_SAMPLES = SR * WINDOW_SEC


# 1) Flask & SocketIO setup
app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

buffer = np.zeros(0, dtype='float32')



@socketio.on('connect')
def on_connect():
    print('📡 Client connected:')
    socketio.emit('connected', {'msg': 'ready'})

@socketio.on('audio_chunk')
def on_chunk(raw_buffer: bytes):
    global buffer

    # 1) decode raw Float32Array.buffer → numpy
    try:
        chunk = np.frombuffer(raw_buffer, dtype='float32')
    except Exception as e:
        print('⚠️ cannot decode chunk:', e)
        return

    # 2) append & truncate
    buffer = np.concatenate([buffer, chunk])[-WINDOW_SAMPLES:]

    # 3) once we have a full window, run detection
    if buffer.size >= WINDOW_SAMPLES:
        try:
            # run_audio expects (np_array, sample_rate)
            result = run_audio((buffer, SR), filename='live_window')
            events = result.get('records', [])
            socketio.emit('live_events', {'events': events})
        except Exception as e:
            print('🔥 model error:', e)
            socketio.emit('live_events', {'error': str(e)})

@socketio.on('disconnect')
def on_disconnect():
    print('❌ Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001)