import os
import tempfile
import uuid
from model.modelanalyse import run
from pydub import AudioSegment

def analyze_recording(file_obj):
    # Determine the file extension from the uploaded filename
    original_ext = os.path.splitext(file_obj.filename)[1].lower()
    
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
            analysis_result = run(wav_file_path)
        except Exception as e:
            print(f"Error during analysis: {e}")
            analysis_result = {"error": str(e)}
        finally:
            # Delete the temporary WAV file whether or not the above steps succeed
            if os.path.exists(wav_file_path):
                os.remove(wav_file_path)
        
        return {"analysis": analysis_result}
    else:
        return {"error": "File conversion failed or file does not exist"}

