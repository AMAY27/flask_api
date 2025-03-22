from flask import Blueprint, request
from flask_cors import cross_origin

sound_analysis = Blueprint('sound_analysis', __name__, url_prefix='/api')

# @sound_analysis.route('/sound_analysis', methods=['POST'])
# @cross_origin()
# def analyze_sound():
