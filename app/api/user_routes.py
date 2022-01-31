from flask import request, jsonify
from webargs.flaskparser import use_args
from marshmallow import Schema, fields
from app import models, schemas, db
from app.api import blueprint
from engine import application_processor as ap

from flask import make_response, jsonify


def make_404(message):
    return make_response(jsonify(message), 404)


@blueprint.route('/users', methods=['POST'])
@use_args(schemas.user_create_request_schema)
def add_user(args):
    user = models.User(name=args['name'])
    db.session.add(user)
    db.session.commit()
    return jsonify(schemas.user_schema.dump(user)), 201


@blueprint.route('/users/<uuid:user_id>', methods=['GET'])
def get_user(user_id):
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested user was not found.')
    return jsonify(schemas.user_schema.dump(user))


@blueprint.route('/users/<uuid:user_id>', methods=['PUT'])
@use_args(schemas.user_update_request_schema)
def update_user(args, user_id):
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested user was not found.')

    for key, val in args.items():
        setattr(user, key, val)
    db.session.add(user)
    db.session.commit()
    return jsonify(schemas.user_schema.dump(user))


@blueprint.route('/users/<uuid:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested user was not found.')

    db.session.delete(user)
    db.session.commit()
    return jsonify(), 204
