import eventlet
eventlet.monkey_patch()

from flask import Flask
import os
from routes import register_routes
import base64
import time
from sound_analysis_services import analyze_live_chunk_inmemory

# ------------------------
# Flask-SocketIO Setup for Live Streaming
# ------------------------
from flask_socketio import SocketIO
# socketio = SocketIO(async_mode="gevent",cors_allowed_origins="*")

app = Flask(__name__)
config_type = os.environ.get('CONFIG_TYPE', 'config.DevelopmentConfig')
app.config.from_object(config_type) 
app = register_routes(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")
# def create_app():
#     app = Flask(__name__)
#     config_type = os.environ.get('CONFIG_TYPE', 'config.DevelopmentConfig')
#     app.config.from_object(config_type)
#     app = register_routes(app)
#     # Initialize SocketIO with the app.
#     app.config['SECRET_KEY'] = 'secret!'
#     socketio.init_app(app)
#     return app


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5001, debug=False, use_reloader=False)

#def create_app():
#    
#    app = Flask(__name__)
#    config_type = os.environ.get('CONFIG_TYPE', 'config.DevelopmentConfig')
#    app.config.from_object(config_type)
#    app = register_routes(app)
#
#    return app
#
#if __name__ == "__main__":
#    app = create_app()
#    # app.run(port=5001, debug=True)
#    app.run(host="0.0.0.0", port=5001, debug=True)


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('message', {'data': 'Connected to live streaming service'})

@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    print("Received audio chunk")
    audio_data = data.get('audio')
    if audio_data:
        audio_bytes = base64.b64decode(audio_data)
        print(f"Received chunk size: {len(audio_bytes)} bytes")
        # Call the in-memory analysis function (assuming .webm as original extension)
        analysis_result = analyze_live_chunk_inmemory(audio_bytes, ".webm")
        events = analysis_result.get('records', [])
        socketio.emit('live_events', {'events': events})
    else:
        socketio.emit('live_events', {'error': 'No audio data received'})


#@socketio.on('audio_chunk')
#def handle_audio_chunk(data):
#    """
#    Receives a base64-encoded audio chunk, writes it to a temporary file,
#    analyzes it using analyze_live_chunk, and emits detected events back.
#    """
#
#    if 'model' not in list_of_models:
#        list_of_models['model'] = get_model(list_of_models["model_class"], list_of_models["config"], list_of_models["weights_path"])
#    
#    audio_data = data.get('audio')
#    if audio_data:
#        # Decode the base64-encoded audio chunk.
#        audio_bytes = base64.b64decode(audio_data)
#        temp_filename = f"temp_{int(time.time()*1000)}.webm"
#        with open(temp_filename, "wb") as f:
#            f.write(audio_bytes)
#        try:
#            analysis_result = analyze_live_chunk(temp_filename)
#            # Assume analysis_result contains a key "records" with a list of detected events.
#            events = analysis_result.get('records', [])
#            socketio.emit('live_events', {'events': events})
#        except Exception as e:
#            print("Error analyzing live chunk:", e)
#            socketio.emit('live_events', {'error': str(e)})
#        finally:
#            if os.path.exists(temp_filename):
#                os.remove(temp_filename)
#    else:
#        socketio.emit('live_events', {'error': 'No audio data received'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')