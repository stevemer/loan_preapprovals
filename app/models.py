"""Contains SQLAlchemy models for the API.

All objects persisted to the database are represented as models.
"""
from sqlalchemy.dialects.postgresql import UUID
from app import db
import enum
import uuid


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    applications = db.relationship(
        'Application',
        backref='rollup',
        lazy='selectin',
        cascade="all,delete-orphan",
    )
    name = db.Column(db.String)


class ApplicantInfo(db.Model):
    """The user-provided info for a loan application."""
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(UUID(as_uuid=True),
                               db.ForeignKey('application.id'),
                               nullable=False)
    application = db.relationship("Application",
                                  back_populates="applicant_info")
    credit_score = db.Column(db.Integer, nullable=False)
    monthly_debt = db.Column(db.Float, nullable=False)
    monthly_income = db.Column(db.Float, nullable=False)
    bankruptcies = db.Column(db.Integer, nullable=False)
    delinquencies = db.Column(db.Integer, nullable=False)
    vehicle_value = db.Column(db.Float, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)


class Offer(db.Model):
    """A loan offer for which the user would be eligible."""
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(UUID(as_uuid=True),
                               db.ForeignKey('application.id'),
                               nullable=False)
    application = db.relationship("Application", back_populates="offer")
    apr = db.Column(db.Float, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    term_length_months = db.Column(db.Integer, nullable=False)


class RejectionReason(enum.IntEnum):
    """The reasons why a user might be ineligible for a loan."""
    EXCESSIVE_BANKRUPTCIES = 1
    EXCESSIVE_DELINQUENCIES = 2
    EXCESSIVE_DEBT_TO_INCOME_RATIO = 3
    EXCESSIVE_LOAN_TO_VALUE_RATIO = 4
    INSUFFICIENT_CREDIT_SCORE = 5


class Rejection(db.Model):
    """A item that has been determined to make the user ineligible for a loan."""
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(UUID(as_uuid=True),
                               db.ForeignKey('application.id'),
                               nullable=False)
    reason = db.Column(db.Enum(RejectionReason), nullable=False)
    __table_args__ = (db.UniqueConstraint('application_id',
                                          'reason',
                                          name='_application_rejection_uc'), )


class ApplicationStatus(enum.IntEnum):
    APPROVED = 1
    DECLINED = 2
    PENDING = 3


class Application(db.Model):
    """An application for a loan. Contains both user-provided info and loan decision."""
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True),
                        db.ForeignKey('users.id'),
                        nullable=False,
                        index=True)
    applicant_info = db.relationship("ApplicantInfo",
                                     back_populates="application",
                                     cascade="all,delete-orphan",
                                     uselist=False)
    status = db.Column(db.Enum(ApplicationStatus))
    offer = db.relationship("Offer",
                            back_populates="application",
                            cascade="all,delete-orphan",
                            uselist=False)
    rejections = db.relationship('Rejection',
                                 backref='rollup',
                                 cascade="all,delete-orphan",
                                 lazy='selectin')
