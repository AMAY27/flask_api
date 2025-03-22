from flask import Blueprint, request
from flask_cors import cross_origin
from sound_analysis_services import analyze_recording

sound_analysis = Blueprint('sound_analysis', __name__, url_prefix='/api')

@sound_analysis.route('/sound_analysis', methods=['POST'])
@cross_origin()
def analyze_sound():
    params = request.get_json()
    return analyze_recording(params)
