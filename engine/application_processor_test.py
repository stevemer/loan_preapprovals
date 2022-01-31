"""Test coverage for the loan processing engine."""
from testing.flask_test_base import FlaskTest
from app import models
from engine import application_processor as ap
from constants import constants
from numpy import testing

def _make_great_applicant_info():
    return models.ApplicantInfo(credit_score=1000.0,
                                monthly_debt=0.0,
                                monthly_income=1000.0,
                                bankruptcies=0,
                                delinquencies=0,
                                vehicle_value=10000.0,
                                loan_amount=2000.0)


class SimpleGoodApplicantTest(FlaskTest):
    """Test with an eligible user in ideal conditions."""

    def test_exactly_maximum_bankruptcies_are_not_declined(self):
        info = _make_great_applicant_info()
        offer, rejection_reasons = ap.process_application(info)
        self.assertEqual(len(rejection_reasons), 0)
        self.assertEqual(offer.apr, 0.02)
        testing.assert_almost_equal(offer.monthly_payment, 29.50, decimal=3)
        self.assertEqual(offer.term_length_months, 72)


class BasicHardCutTests(FlaskTest):
    """Test the simple rejection cases in isolation."""

    def test_exactly_maximum_bankruptcies_are_not_declined(self):
        info = _make_great_applicant_info()
        info.bankruptcies = constants.MAXIMUM_BANKRUPTCIES
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_BANKRUPTCIES not in
                        rejection_reasons)

    def test_excessive_bankruptcies_are_declined(self):
        info = _make_great_applicant_info()
        info.bankruptcies = constants.MAXIMUM_BANKRUPTCIES + 1
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(
            models.RejectionReason.EXCESSIVE_BANKRUPTCIES in rejection_reasons)
        self.assertIsNone(offer)

    def test_exactly_maximum_delinquencies_are_not_declined(self):
        info = _make_great_applicant_info()
        info.delinquencies = constants.MAXIMUM_DELINQUENCIES
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DELINQUENCIES not in
                        rejection_reasons)

    def test_excessive_delinquencies_are_declined(self):
        info = _make_great_applicant_info()
        info.delinquencies = constants.MAXIMUM_DELINQUENCIES + 1
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DELINQUENCIES in
                        rejection_reasons)
        self.assertIsNone(offer)

    def test_very_excessive_debt_to_income_is_declined(self):
        info = _make_great_applicant_info()
        info.monthly_debt = 99999.99
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)

    def test_loan_amount_gt_max_value_ratio_is_declined(self):
        info = _make_great_applicant_info()
        info.loan_amount = 999999.99
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_LOAN_TO_VALUE_RATIO in
                        rejection_reasons)
        self.assertIsNone(offer)

    def test_outside_credit_bands_is_declined(self):
        info = _make_great_applicant_info()
        info.credit_score = 0
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.INSUFFICIENT_CREDIT_SCORE in
                        rejection_reasons)
        self.assertIsNone(offer)


class MultipleCutReasonTests(FlaskTest):
    """Test that multiple hard cut reasons trigger together."""

    def test_bankruptcies_and_delinquencies_trigger_together(self):
        info = _make_great_applicant_info()
        info.bankruptcies = constants.MAXIMUM_BANKRUPTCIES + 1
        info.delinquencies = constants.MAXIMUM_DELINQUENCIES + 1
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(
            models.RejectionReason.EXCESSIVE_BANKRUPTCIES in rejection_reasons)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DELINQUENCIES in
                        rejection_reasons)
        self.assertIsNone(offer)

    def test_loan_amount_gt_max_value_and_debt_to_income_trigger_together(
            self):
        info = _make_great_applicant_info()
        info.loan_amount = 999999.99
        info.monthly_debt = 99999.99
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_LOAN_TO_VALUE_RATIO in
                        rejection_reasons)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)

    def test_bad_credit_score_includes_preloan_debt_to_income_check(self):
        info = models.ApplicantInfo(credit_score=4,
                                    monthly_debt=1000.0 *
                                    constants.MAXIMUM_DEBT_TO_INCOME_RATIO *
                                    (1.01),
                                    monthly_income=1000.0,
                                    bankruptcies=3,
                                    delinquencies=5,
                                    vehicle_value=200.0,
                                    loan_amount=30000.0)
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.INSUFFICIENT_CREDIT_SCORE in
                        rejection_reasons)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)

    def test_bad_credit_score_precludes_postloan_debt_to_income_check(self):
        info = models.ApplicantInfo(credit_score=4,
                                    monthly_debt=1000.0 *
                                    constants.MAXIMUM_DEBT_TO_INCOME_RATIO *
                                    (0.999),
                                    monthly_income=1000.0,
                                    bankruptcies=3,
                                    delinquencies=5,
                                    vehicle_value=200.0,
                                    loan_amount=30000.0)
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.INSUFFICIENT_CREDIT_SCORE in
                        rejection_reasons)
        self.assertFalse(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                         in rejection_reasons)
        self.assertIsNone(offer)

    def test_all_reasons_except_for_credit_score(self):
        info = models.ApplicantInfo(credit_score=4,
                                    monthly_debt=4000.0,
                                    monthly_income=1000.0,
                                    bankruptcies=3,
                                    delinquencies=5,
                                    vehicle_value=200.0,
                                    loan_amount=30000.0)
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(
            models.RejectionReason.EXCESSIVE_BANKRUPTCIES in rejection_reasons)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DELINQUENCIES in
                        rejection_reasons)
        self.assertTrue(models.RejectionReason.INSUFFICIENT_CREDIT_SCORE in
                        rejection_reasons)
        self.assertTrue(models.RejectionReason.EXCESSIVE_LOAN_TO_VALUE_RATIO in
                        rejection_reasons)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)


class CreditBandRiskBasedRateTests(FlaskTest):
    """Make sure we select the correct rates."""

    def test_first_eligible_rate_is_selected(self):
        info = _make_great_applicant_info()
        info.credit_score = constants.CREDIT_BANDS[0][
            'minimum_score_required'] + 1
        offer, rejection_reasons = ap.process_application(info)
        self.assertEqual(constants.CREDIT_BANDS[0]['apr'], offer.apr)


class DebtToIncomeLogicTests(FlaskTest):
    """Make sure debt-to-income is calculated correctly."""

    def test_preexisting_excessive_debt_is_declined(self):
        info = models.ApplicantInfo(credit_score=1000,
                                    monthly_debt=100.0 *
                                    constants.MAXIMUM_DEBT_TO_INCOME_RATIO *
                                    (1.01),
                                    monthly_income=100.0,
                                    bankruptcies=0,
                                    delinquencies=0,
                                    vehicle_value=10000.0,
                                    loan_amount=20.0)
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)

    def test_excessive_debt_only_after_tenet_loan_is_declined(self):
        info = models.ApplicantInfo(credit_score=1000.0,
                                    monthly_debt=100.0 *
                                    constants.MAXIMUM_DEBT_TO_INCOME_RATIO *
                                    (0.8),
                                    monthly_income=0.0,
                                    bankruptcies=0,
                                    delinquencies=0,
                                    vehicle_value=99999999.0,
                                    loan_amount=9999999.0)
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)

    def test_excessive_debt_only_after_tenet_loan_is_declined(self):
        info = models.ApplicantInfo(credit_score=1000.0,
                                    monthly_debt=100.0 *
                                    constants.MAXIMUM_DEBT_TO_INCOME_RATIO *
                                    (0.8),
                                    monthly_income=0.0,
                                    bankruptcies=0,
                                    delinquencies=0,
                                    vehicle_value=99999999.0,
                                    loan_amount=9999999.0)
        offer, rejection_reasons = ap.process_application(info)
        self.assertTrue(models.RejectionReason.EXCESSIVE_DEBT_TO_INCOME_RATIO
                        in rejection_reasons)
        self.assertIsNone(offer)


class LoanValueCalculationTests(FlaskTest):
    """Briefly make sure loan payment calculation remains accurate."""

    def test_correct_value_for_simple_loan(self):
        info = _make_great_applicant_info()
        info.credit_score = 1000
        info.loan_amount = 10000
        offer, rejection_reasons = ap.process_application(info)
        testing.assert_almost_equal(offer.monthly_payment, 147.504, decimal=3)
