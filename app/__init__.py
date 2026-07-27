from flask import Flask
from configs import Config
from app.core.ai_service import GenAIService

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route('/')
    def home():
        return f"<h1>server is on</h1>"

    return app

app = create_app()

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)