from testing.flask_test_base import FlaskTest
from constants import constants
import hashlib
import os


class CreditBandValidationTests(FlaskTest):
    """Validates credit band config."""

    def test_credit_bands_are_ordered_desc_by_minimum_credit_score(self):
        band_scores = [
            band['minimum_score_required'] for band in constants.CREDIT_BANDS
        ]
        self.assertEqual(len(band_scores),
                         len(set(band_scores)))  # no dups allowed
        self.assertListEqual(band_scores, sorted(band_scores, reverse=True))

    def test_credit_bands_are_ordered_asc_by_apr(self):
        band_aprs = [band['apr'] for band in constants.CREDIT_BANDS]
        self.assertEqual(len(band_aprs),
                         len(set(band_aprs)))  # no dups allowed
        self.assertListEqual(band_aprs, sorted(band_aprs))

    def test_credit_bands_all_have_correct_keys_and_types(self):
        band_scores = [
            band['minimum_score_required'] for band in constants.CREDIT_BANDS
        ]
        band_aprs = [band['apr'] for band in constants.CREDIT_BANDS]
        self.assertTrue(all(type(score) == int for score in band_scores))
        self.assertTrue(all(type(apr) == float for apr in band_aprs))

    def test_no_credit_score_above_1000(self):
        band_scores = [
            band['minimum_score_required'] for band in constants.CREDIT_BANDS
        ]
        self.assertFalse(any(score >= 1000 for score in band_scores))

    def test_no_credit_score_below_0(self):
        band_scores = [
            band['minimum_score_required'] for band in constants.CREDIT_BANDS
        ]
        self.assertFalse(any(score < 0 for score in band_scores))

    def test_no_apr_below_0_percent(self):
        band_aprs = [band['apr'] for band in constants.CREDIT_BANDS]
        self.assertFalse(any(apr < 0 for apr in band_aprs))

    def test_no_apr_above_30_percent(self):
        band_aprs = [band['apr'] for band in constants.CREDIT_BANDS]
        self.assertFalse(any(apr > 0.30 for apr in band_aprs))


class GoldenConstantsTest(FlaskTest):
    """Protects constants against accidental changes."""

    def test_digest_matches_checksum(self):
        constants_filename = os.path.join(os.path.dirname(__file__),
                                          'constants.py')
        constants_checksum_filename = os.path.join(os.path.dirname(__file__),
                                                   'constants_checksum')
        digest = hashlib.md5(open(constants_filename, 'rb').read()).digest()
        checked_in_digest = open(constants_checksum_filename, 'rb').read()
        self.assertEqual(
            digest, checked_in_digest,
            'Financial constants have been modified. Please get signoff from business logic owner before submission, then update digest.'
        )
