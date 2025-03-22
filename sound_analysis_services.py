import os
from model.modelanalyse import run

def analyze_recording(params):
    backend_directory = os.path.dirname(os.path.abspath(__file__))
    recordings_directory = os.path.join(backend_directory, "recordings")
    file_path = os.path.join(recordings_directory, "Recording (8).wav")
    run(file_path)
