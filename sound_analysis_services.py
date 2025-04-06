import os
import tempfile
import uuid
from model.modelanalyse import run, get_model, list_of_models
from pydub import AudioSegment
import librosa
from model.modelanalyselive import run_audio
#from flask_socketio import SocketIO, emit

def analyze_recording(file_obj):
    # Load the model
    
    # Determine the file extension from the uploaded filename
    original_ext = os.path.splitext(file_obj.filename)[1].lower()
    print(f"File path: {file_obj.filename}")
    
    # Define the recordings folder relative to this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    recordings_dir = os.path.join(base_dir, "model", "recordings")
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Generate a unique file name for the original upload
    unique_filename = f"{uuid.uuid4()}{original_ext}"
    original_file_path = os.path.join(recordings_dir, unique_filename)
    
    # Save the uploaded file to the recordings folder
    file_obj.save(original_file_path)
    print(f"File saved to: {original_file_path}")
    
    # Convert file to WAV if necessary
    if original_ext != ".wav":
        # Generate a unique filename for the converted WAV file
        wav_filename = f"{uuid.uuid4()}.wav"
        wav_file_path = os.path.join(recordings_dir, wav_filename)
        try:
            # Load the audio file using pydub (format without the dot)
            audio = AudioSegment.from_file(original_file_path, format=original_ext.replace('.', ''))
            # Export the audio in WAV format
            audio.export(wav_file_path, format="wav")
            print(f"File converted to WAV: {wav_file_path}")
        except Exception as e:
            print(f"Error processing file: {e}")
            wav_file_path = None
        finally:
            # Remove the original non-wav file after conversion
            try:
                os.remove(original_file_path)
            except Exception as ex:
                print(f"Error deleting original file: {ex}")
    else:
        wav_file_path = original_file_path
        print(f"File is already in WAV format: {wav_file_path}")
    
    if wav_file_path and os.path.exists(wav_file_path):
        try:
            # Perform analysis on the WAV file
            analysis_result = run(wav_file_path, filename=file_obj.filename)
            print(f"Analysis result: {analysis_result}")
        except FileExistsError as fee:
            print(f"File Exists error: {fee}")
            analysis_result = {"error": str(fee)}
        except Exception as e:
            print(f"Error during analysis: {e}")
            analysis_result = {"error": str(e)}
        finally:
            # Delete the temporary WAV file whether or not the above steps succeed
            if os.path.exists(wav_file_path):
                os.remove(wav_file_path)
            print(f"Temporary WAV file deleted: {wav_file_path}")
        
        return analysis_result
    else:
        return {"error": "File conversion failed or file does not exist"}
    

# ------------------------
# New Live Streaming Service
# ------------------------
# This new service processes live audio chunks without needing a file_obj.



from io import BytesIO

def analyze_live_chunk_inmemory(audio_bytes, original_ext):
    """
    Processes an audio chunk in memory.
    :param audio_bytes: The raw audio bytes (from the live chunk)
    :param original_ext: Original extension (e.g. ".webm")
    :return: Analysis result (dict)
    """
    # Ensure the model is loaded:
    if 'model' not in list_of_models:
        list_of_models['model'] = get_model(
            list_of_models["model_class"],
            list_of_models["config"],
            list_of_models["weights_path"]
        )
    
    # Use pydub to load the audio from the in-memory bytes:
    audio_file = BytesIO(audio_bytes)
    try:
        # pydub requires the format string without the dot
        audio_segment = AudioSegment.from_file(audio_file, format=original_ext.replace('.', ''))
    except Exception as e:
        print(f"Error processing audio segment in memory: {e}")
        return {"error": str(e)}
    
    # Export to WAV in memory:
    wav_io = BytesIO()
    try:
        audio_segment.export(wav_io, format="wav")
    except Exception as e:
        print(f"Error exporting to WAV in memory: {e}")
        return {"error": str(e)}
    wav_io.seek(0)
    
    try:
        # Load the WAV data using librosa (using soundfile under the hood)
        y = librosa.load(wav_io)
    except Exception as e:
        print(f"Error loading audio from in-memory WAV file: {e}")
        return {"error": str(e)}
    
    # Now run the analysis on the in-memory audio data.
    return run_audio(y, filename="inmemory_chunk")


def analyze_live_chunk(file_path):
    """
    Processes a temporary audio file (from a live stream chunk), converts it to WAV if needed,
    runs the analysis model, and returns the analysis result.
    """
    # Determine the file extension from the file path
    original_ext = os.path.splitext(file_path)[1].lower()
    print(f"Processing live file: {file_path}")
    
    # Define the recordings folder relative to this file's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    recordings_dir = os.path.join(base_dir, "model", "recordings")
    os.makedirs(recordings_dir, exist_ok=True)
    
    # If the file is not in WAV format, convert it.
    if original_ext != ".wav":
        wav_filename = f"{uuid.uuid4()}.wav"
        wav_file_path = os.path.join(recordings_dir, wav_filename)
        try:
            audio = AudioSegment.from_file(file_path, format=original_ext.replace('.', ''))
            audio.export(wav_file_path, format="wav")
            print(f"Live file converted to WAV: {wav_file_path}")
        except Exception as e:
            print(f"Error processing live file: {e}")
            wav_file_path = None
        finally:
            # Remove the original temporary file
            try:
                os.remove(file_path)
            except Exception as ex:
                print(f"Error deleting original live file: {ex}")
    else:
        wav_file_path = file_path
        print(f"Live file is already in WAV format: {wav_file_path}")
    
    if wav_file_path and os.path.exists(wav_file_path):
        try:
            # Perform analysis on the WAV file using your existing run() function.
            analysis_result = run(wav_file_path, filename=os.path.basename(file_path))
            print(f"Live analysis result: {analysis_result}")
        except Exception as e:
            print(f"Error during live analysis: {e}")
            analysis_result = {"error": str(e)}
        finally:
            if os.path.exists(wav_file_path):
                os.remove(wav_file_path)
                print(f"Temporary live WAV file deleted: {wav_file_path}")
        return analysis_result
    else:
        return {"error": "Live file conversion failed or file does not exist"}


# ------------------------
# Flask-SocketIO Setup for Live Streaming
# ------------------------
#from socketio_instance import socketio
#import base64
#import time
#
## Create the SocketIO instance. (For a real application, consider initializing this in your main app.)
#
#@socketio.on('connect')
#def handle_connect():
#    print('Client connected')
#    socketio.emit('message', {'data': 'Connected to live streaming service'})
#
#@socketio.on('audio_chunk')
#def handle_audio_chunk(data):
#    """
#    Receives a base64-encoded audio chunk, writes it to a temporary file,
#    analyzes it using analyze_live_chunk, and emits detected events back.
#    """
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
#
#@socketio.on('disconnect')
#def handle_disconnect():
#    print('Client disconnected')

