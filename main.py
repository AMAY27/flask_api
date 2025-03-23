from flask import Flask
import os
from routes import register_routes

def create_app():
    app = Flask(__name__)
    config_type = os.environ.get('CONFIG_TYPE', 'config.DevelopmentConfig')
    app.config.from_object(config_type)
    app = register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    # app.run(port=5001, debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)