import sound_analysis_controller

def register_routes(app):
    app.register_blueprint(sound_analysis_controller.sound_analysis)
    return app