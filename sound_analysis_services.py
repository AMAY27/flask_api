import os
import tempfile
from model.modelanalyse import run
from pydub import AudioSegment

def analyze_recording(file_obj):
    # Determine the file extension from the uploaded filename
    original_ext = os.path.splitext(file_obj.filename)[1].lower()
    
    # Create a temporary file to save the original upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=original_ext) as tmp:
        original_file_path = tmp.name
        file_obj.save(original_file_path)
    
    # Convert file to WAV if necessary
    if original_ext != ".wav":
        # Create a temporary filename for the converted WAV file
        wav_file_path = original_file_path + ".wav"
        try:
            # Load the audio file using pydub (specify format without the dot)
            audio = AudioSegment.from_file(original_file_path, format=original_ext.replace('.', ''))
            # Export the audio in WAV format
            audio.export(wav_file_path, format="wav")
        except Exception as e:
            # Clean up original file if conversion fails
            os.remove(original_file_path)
            raise e
        finally:
            # Remove the original non-wav file
            if os.path.exists(original_file_path):
                os.remove(original_file_path)
    else:
        wav_file_path = original_file_path
    
    try:
        # Perform analysis on the WAV file
        analysis_result = run(wav_file_path)
        
        # Upload the WAV file to AWS S3
        # s3_client = boto3.client('s3')
        # bucket_name = 'your-bucket-name'  # Replace with your actual bucket name
        # s3_key = f"recordings/{uuid.uuid4()}.wav"
        # s3_client.upload_file(wav_file_path, bucket_name, s3_key)
    finally:
        # Delete the temporary WAV file whether or not the above steps succeed
        if os.path.exists(wav_file_path):
            os.remove(wav_file_path)
    
    # return {"analysis": analysis_result, "s3_key": s3_key}
    return {"analysis": analysis_result}

