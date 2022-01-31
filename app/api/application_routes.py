from flask import request, jsonify
from webargs.flaskparser import use_args
from marshmallow import Schema, fields
from app import models, schemas, db
from app.api import blueprint
from engine import application_processor as ap

from flask import make_response, jsonify


def make_404(message):
    return make_response(jsonify(message), 404)


@blueprint.route('/users/<uuid:user_id>/applications', methods=['POST'])
@use_args(schemas.ApplicantInfoSchema())
def submit_application(applicant_info_args, user_id):
    # NOTE: Rate-limiting would be a useful feature for this API.
    # Might also consider metrics on outlier users with excessive applications.
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested user was not found.')
    applicant_info = models.ApplicantInfo(**applicant_info_args)

    # Evaluate the application so we know whether we can make an offer.
    offer, rejection_reasons = ap.process_application(applicant_info)

    application = models.Application(user_id=user_id,
                                     applicant_info=applicant_info)
    if offer is not None:
        application.status = models.ApplicationStatus.APPROVED
        application.offer = offer
    else:
        application.status = models.ApplicationStatus.DECLINED
        application.rejections = [
            models.Rejection(reason=rejection_reason)
            for rejection_reason in rejection_reasons
        ]

    # Save the application data along with any offer or rejections.
    db.session.add(application)
    db.session.commit()

    return jsonify(schemas.application_schema.dump(application)), 201


@blueprint.route('/users/<uuid:user_id>/applications/<uuid:application_id>',
                 methods=['PUT'])
@use_args(schemas.ApplicantInfoSchema(partial=True))
def update_application(applicant_info_args, user_id, application_id):
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested application was not found.')
    application = models.Application.query.get(application_id)
    if application is None:
        return make_404('the requested application was not found.')

    if user.id != application.user_id:
        return make_404('the requested application was not found.')

    for key, val in applicant_info_args.items():
        setattr(application.applicant_info, key, val)

    # Evaluate the application so we know whether we can make an offer.
    offer, rejection_reasons = ap.process_application(
        application.applicant_info)

    if offer is not None:
        application.status = models.ApplicationStatus.APPROVED
        application.offer = offer
        application.rejections = []
    else:
        application.status = models.ApplicationStatus.DECLINED
        application.offer = None
        existing_reasons = set([r.reason for r in application.rejections])
        updated_reasons = set(rejection_reasons)
        intersect_list = (existing_reasons & updated_reasons)
        to_remove = (existing_reasons ^ intersect_list)
        to_add = (updated_reasons ^ intersect_list)

        for rejection in application.rejections:
            if rejection.reason in to_remove:
                db.session.delete(rejection)

        for rejection_reason in to_add:
            application.rejections.append(
                models.Rejection(reason=rejection_reason))

    # Save the application data along with any offer or rejections.
    db.session.add(application)
    db.session.commit()

    return jsonify(schemas.application_schema.dump(application)), 200


@blueprint.route('/users/<uuid:user_id>/applications/<uuid:application_id>',
                 methods=['GET'])
def get_application(user_id, application_id):
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested application was not found.')

    application = models.Application.query.get(application_id)
    if application is None:
        return make_404('the requested application was not found.')

    if user.id != application.user_id:
        return make_404('the requested application was not found.')

    return jsonify(schemas.application_schema.dump(application))


@blueprint.route('/users/<uuid:user_id>/applications/<uuid:application_id>',
                 methods=['DELETE'])
def delete_application(user_id, application_id):
    user = models.User.query.get(user_id)
    if user is None:
        return make_404('the requested application was not found.')

    application = models.Application.query.get(application_id)
    if application is None:
        return make_404('the requested application was not found.')

    if user.id != application.user_id:
        return make_404('the requested application was not found.')

    db.session.delete(application)
    db.session.commit()

    return jsonify(), 204
