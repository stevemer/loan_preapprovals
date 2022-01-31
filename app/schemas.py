"""Contains Marshmallow schemas for the API.

All objects that the user sees or sends are represented as schemas.
"""

from app import ma
from marshmallow import Schema, fields, validate

_ERROR_MSG_TMPL = {
    'required': 'Missing data for required field \'{field_name}\'.',
    'null': 'Field \'{field_name}\' may not be null.',
    'validator_failed': 'Invalid value for \'{field_name}\'.',
}


def _build_err_msg_dict(field_name):
    return {
        key: value.format(field_name=field_name)
        for key, value in _ERROR_MSG_TMPL.items()
    }


class ApplicantInfoSchema(Schema):
    credit_score = fields.Integer(
        required=True, error_messages=_build_err_msg_dict('credit_score'))
    monthly_debt = fields.Float(
        required=True, error_messages=_build_err_msg_dict('monthly_debt'))
    monthly_income = fields.Float(
        required=True, error_messages=_build_err_msg_dict('monthly_income'))
    bankruptcies = fields.Integer(
        required=True, error_messages=_build_err_msg_dict('bankruptcies'))
    delinquencies = fields.Integer(
        required=True, error_messages=_build_err_msg_dict('delinquencies'))
    vehicle_value = fields.Float(
        required=True, error_messages=_build_err_msg_dict('vehicle_value'))
    loan_amount = fields.Float(
        required=True, error_messages=_build_err_msg_dict('loan_amount'))


applicant_info_schema = ApplicantInfoSchema()
applicant_infos_schema = ApplicantInfoSchema(many=True)


class OfferSchema(Schema):
    apr = fields.Float()
    monthly_payment = fields.Float()
    term_length_months = fields.Integer()


offer_schema = OfferSchema()
offers_schema = OfferSchema(many=True)


class RejectionSchema(Schema):
    reason = fields.Function(lambda obj: obj.reason.name)


class ApplicationSchema(Schema):
    id = fields.UUID()
    status = fields.Function(lambda obj: obj.status.name)
    applicant_info = fields.Nested(ApplicantInfoSchema)
    offer = fields.Nested(OfferSchema)
    rejections = fields.Nested(RejectionSchema, many=True)


application_schema = ApplicationSchema()
applications_schema = ApplicationSchema(many=True)


class UserSchema(Schema):
    name = fields.String()
    id = fields.UUID()
    applications = fields.Nested(
        ApplicationSchema(only=('id', 'status'), many=True))


user_schema = UserSchema()
users_schema = UserSchema(many=True)


class UserCreateRequestSchema(Schema):
    name = fields.String(required=True,
                         validate=validate.Length(min=1),
                         error_messages=_build_err_msg_dict('name'))


class UserUpdateRequestSchema(Schema):
    name = fields.String(error_messages=_build_err_msg_dict('name'))


user_create_request_schema = UserCreateRequestSchema()
user_update_request_schema = UserUpdateRequestSchema()
