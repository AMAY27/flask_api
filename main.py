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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("live-audio")

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet' ,cors_allowed_origins="*")

# rolling buffer for last 4 s of audio
SR = 44100
WINDOW_SECONDS = 4
WINDOW_SAMPLES = SR * WINDOW_SECONDS
_buffer = np.zeros(0, dtype=np.float32)

@socketio.on('connect')
def on_connect():
    print('📡 Client connected:')
    socketio.emit('connected', {'msg': 'ready'})

@socketio.on('audio_chunk')
def on_chunk(raw_data):

    global _buffer
    try:
        chunk = np.frombuffer(raw_data, dtype=np.float32)
    except Exception as e:
        logger.error(f"Cannot decode chunk: {e}")
        return

    # append & cap to WINDOW_SAMPLES
    _buffer = np.concatenate([_buffer, chunk])

    # once we have full buffer, run model
    while _buffer.shape[0] >= WINDOW_SAMPLES:
        segment = _buffer[:WINDOW_SAMPLES]
        _buffer = _buffer[WINDOW_SAMPLES:]
        try:
            # run_audio takes (data_array, sample_rate)
            result = run_audio((segment, SR))
            socketio.emit('live_events', result)
        except Exception as e:
            logger.exception("Error running model")
            socketio.emit("live_events", {"error": str(e)})


@socketio.on('disconnect')
def on_disconnect():
    print('❌ Client disconnected')

if __name__ == '__main__':
    if 'model' not in list_of_models:
        list_of_models['model'] = get_model(
            list_of_models["model_class"],
            list_of_models["config"],
            list_of_models["weights_path"]
        )
    socketio.run(app, host='0.0.0.0', port=5001)