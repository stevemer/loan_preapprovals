from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from webargs.flaskparser import parser
from flask import jsonify
from flask_restful import abort
import os

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()


def create_app():

    app = Flask(__name__)
    # https://stackoverflow.com/questions/62688256/sqlalchemy-exc-nosuchmoduleerror-cant-load-plugin-sqlalchemy-dialectspostgre
    database_url = os.environ.get('DATABASE_URL')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    # Importing within this function avoids circular imports.
    from app.api import blueprint as api_blueprint
    app.register_blueprint(api_blueprint)

    @app.errorhandler(422)
    def custom_handler(err):
        return jsonify({
            'status': 422,
            'title': 'One or more parameters did not validate.',
            'messages': err.data['meta']['messages']['json'],
            'data': err.data['meta']['data'],
            'valid_data': err.data['meta']['valid_data'],
        }), 422

    @parser.error_handler
    def handle_error(error, req, schema, *, error_status_code, error_headers):
        abort(422,
              meta={
                  'data': error.data,
                  'messages': error.messages,
                  'valid_data': error.valid_data,
              })

    return app
