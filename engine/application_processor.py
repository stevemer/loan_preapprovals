"""Loan processing logic."""
from constants import constants
import numpy_financial as npf
from app import models


def process_application(applicant_info):
    """Returns a tuple containing either an offer or a list of rejection reasons."""
    reasons_to_decline = []

    # Check for ineligible loans according to current criteria.
    if applicant_info.bankruptcies > constants.MAXIMUM_BANKRUPTCIES:
        reasons_to_decline.append(models.RejectionReason.EXCESSIVE_BANKRUPTCIES)

    if applicant_info.delinquencies > constants.MAXIMUM_DELINQUENCIES:
        reasons_to_decline.append(models.RejectionReason.EXCESSIVE_DELINQUENCIES)

    eligible_rate = None
    for band in constants.CREDIT_BANDS:
        if applicant_info.credit_score >= band['minimum_score_required']:
            eligible_rate = band['apr']
            break

    if eligible_rate is None:
        reasons_to_decline.append(models.RejectionReason.INSUFFICIENT_CREDIT_SCORE)

    loan_to_value_ratio = applicant_info.loan_amount / applicant_info.vehicle_value
    if loan_to_value_ratio > 1:
        reasons_to_decline.append(models.RejectionReason.EXCESSIVE_LOAN_TO_VALUE_RATIO)

    tenet_monthly_payment = None
    if eligible_rate is None:
        debt_to_income_ratio = applicant_info.monthly_debt / applicant_info.monthly_income
        if debt_to_income_ratio > constants.MAXIMUM_DEBT_TO_INCOME_RATIO:
            reasons_to_decline.append(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO)
    else:
        # Calculate the appropriate loan.
        principal = applicant_info.loan_amount
        rate = eligible_rate / 12
        periods = constants.LOAN_LENGTH_IN_MONTHS
        tenet_monthly_payment = -1 * npf.pmt(rate, periods, principal)
        new_monthly_debt = tenet_monthly_payment + applicant_info.monthly_debt
        new_debt_to_income_ratio = new_monthly_debt / applicant_info.monthly_income
        if new_debt_to_income_ratio > constants.MAXIMUM_DEBT_TO_INCOME_RATIO:
            reasons_to_decline.append(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO)

    if len(reasons_to_decline) > 0:
        return None, reasons_to_decline
    else:
        return models.Offer(apr=eligible_rate,
                     monthly_payment=tenet_monthly_payment,
                     term_length_months=constants.LOAN_LENGTH_IN_MONTHS), []
