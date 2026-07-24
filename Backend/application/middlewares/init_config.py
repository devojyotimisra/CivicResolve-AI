from application.helpers.config import Config


def init_config(app):
    app.state.config = Config
