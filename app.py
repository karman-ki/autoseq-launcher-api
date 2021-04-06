import click
import logging
from flask import Flask, Blueprint
from flask_restplus import Resource
from flask_cors import CORS


import settings
from api.restplus import api
from api.task_manager.endpoints.cr_task_manager import ctm as task_manager_namespace

from database import db


log = logging.getLogger(__name__)


def configure_app(flask_app):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.SQLALCHEMY_TRACK_MODIFICATIONS
    flask_app.config['SWAGGER_UI_DOC_EXPANSION'] = settings.RESTPLUS_SWAGGER_UI_DOC_EXPANSION
    flask_app.config['RESTPLUS_VALIDATE'] = settings.RESTPLUS_VALIDATE
    flask_app.config['RESTPLUS_MASK_SWAGGER'] = settings.RESTPLUS_MASK_SWAGGER

    flask_app.config['REF_GENOME_PATH'] = settings.MOUNT_REF_GENOME_PATH
    flask_app.config['LIB_PATH'] = settings.MOUNT_LIB_PATH
    flask_app.config['SCRATCH_PATH'] = settings.MOUNT_SCRATCH_PATH
    flask_app.config['PROBIO'] = settings.MOUNT_POINT_PROBIO
    flask_app.config['PSFF'] = settings.MOUNT_POINT_PSFF

    flask_app.config['ANCHORAGE'] = {'address': settings.ANCHORAGE_ADDR, 'username': settings.ANCHORAGE_USERNAME, 'password': settings.ANCHORAGE_PWD}
    flask_app.config['SCALAR'] = {'address': settings.SCALAR_ADDR, 'username': settings.SCALAR_USERNAME, 'password': settings.SCALAR_PWD}
    flask_app.config['VECTOR'] = {'address': settings.VECTOR_ADDR, 'username': settings.VECTOR_USERNAME, 'password': settings.VECTOR_PWD}


def initialize_app(flask_app):
    configure_app(flask_app)
    blueprint = Blueprint('api', __name__, url_prefix='/api')
    api.init_app(blueprint)
    api.add_namespace(task_manager_namespace)
    flask_app.register_blueprint(blueprint)
    db.init_app(flask_app)

app = Flask(__name__)
CORS(app)


@click.command()
@click.option('-p', '--port', type=int, default=8100)
def main(port):
    initialize_app(app)
    log.info('>>>>> Starting CTM development server at http://{}/api/ <<<<<'.format(app.config['SERVER_NAME']))
    app.run(debug=settings.FLASK_DEBUG, port=port, host='0.0.0.0')

if __name__ == "__main__":
    main()