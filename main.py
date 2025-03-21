from flask import Flask
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['CONFIG_TYPE'])
    app = register_routes(app)

    return app

app = Flask(__name__)
app = register_routes(app)
if __name__ == "__main__":
    # app.run(port=5001, debug=True)
    app.run(host="0.0.0.0", port=5001, debug=True)