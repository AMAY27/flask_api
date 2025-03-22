from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from sound_analysis_services import analyze_recording

sound_analysis = Blueprint('sound_analysis', __name__, url_prefix='/api')

@sound_analysis.route('/sound_analysis', methods=['POST'])
@cross_origin()
def analyze_sound():
    if 'wavfile' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    wav_file = request.files['wavfile']
    result = analyze_recording(wav_file)
    return jsonify(result)
