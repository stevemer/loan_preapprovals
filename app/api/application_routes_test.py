# TODO DO NOT SUBMIT
from testing import flask_test_base
from app import models
import json

_STRONG_APPLICATION = {
    'bankruptcies': 0,
    'credit_score': 1000,
    'monthly_debt': 0,
    'loan_amount': 399,
    'vehicle_value': 2000,
    'monthly_income': 4444444,
    'delinquencies': 0,
}

_WEAK_APPLICATION = {
    'bankruptcies': 3,
    'credit_score': 333,
    'monthly_debt': 220,
    'loan_amount': 399,
    'vehicle_value': 2000,
    'monthly_income': 4444444,
    'delinquencies': 33,
}


class ApplicationCreationTests(flask_test_base.FlaskTest):

    def test_create_declined_offer(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _WEAK_APPLICATION)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['status'], 'DECLINED')

        self.assertEqual(response.json['applicant_info'], _WEAK_APPLICATION)
        self.assertIsNone(response.json['offer'])
        self.assertEqual(response.json['rejections'],
                         [{
                             'reason': 'EXCESSIVE_BANKRUPTCIES'
                         }, {
                             'reason': 'EXCESSIVE_DELINQUENCIES'
                         }, {
                             'reason': 'INSUFFICIENT_CREDIT_SCORE'
                         }])

    def test_create_accepted_offer(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _STRONG_APPLICATION)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['status'], 'APPROVED')
        self.assertIsNotNone(response.json['offer'])
        self.assertEqual(response.json['rejections'], [])

    def test_create_no_params_is_rejected(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json, {
                'data': {},
                'messages': {
                    'bankruptcies':
                    ["Missing data for required field 'bankruptcies'."],
                    'credit_score':
                    ["Missing data for required field 'credit_score'."],
                    'delinquencies':
                    ["Missing data for required field 'delinquencies'."],
                    'loan_amount':
                    ["Missing data for required field 'loan_amount'."],
                    'monthly_debt':
                    ["Missing data for required field 'monthly_debt'."],
                    'monthly_income':
                    ["Missing data for required field 'monthly_income'."],
                    'vehicle_value':
                    ["Missing data for required field 'vehicle_value'."]
                },
                'status': 422,
                'title': 'One or more parameters did not validate.',
                'valid_data': {}
            })

    def test_create_with_some_params_is_rejected(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications', {
            'bankruptcies': 0,
            'credit_score': 1000,
            'monthly_debt': 0,
        })
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json, {
                'data': {
                    'bankruptcies': 0,
                    'credit_score': 1000,
                    'monthly_debt': 0
                },
                'messages': {
                    'delinquencies':
                    ["Missing data for required field 'delinquencies'."],
                    'loan_amount':
                    ["Missing data for required field 'loan_amount'."],
                    'monthly_income':
                    ["Missing data for required field 'monthly_income'."],
                    'vehicle_value':
                    ["Missing data for required field 'vehicle_value'."]
                },
                'status': 422,
                'title': 'One or more parameters did not validate.',
                'valid_data': {
                    'bankruptcies': 0,
                    'credit_score': 1000,
                    'monthly_debt': 0.0
                }
            })


class ApplicationGetTests(flask_test_base.FlaskTest):

    def test_get_valid_application(self):
        user_response = self.post('/users', {'name': 'steve'})
        app_response = self.post(
            '/users/' + user_response.json['id'] + '/applications',
            _WEAK_APPLICATION)
        response = self.get('/users/' + user_response.json['id'] +
                            '/applications/' + app_response.json['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['applicant_info'], _WEAK_APPLICATION)
        self.assertIn('offer', response.json.keys())
        self.assertIn('status', response.json.keys())
        self.assertIn('rejections', response.json.keys())

    def test_get_invalid_application(self):
        user_response = self.post('/users', {'name': 'steve'})
        app_response = self.post(
            '/users/' + user_response.json['id'] + '/applications',
            _WEAK_APPLICATION)
        response = self.get('/users/' + user_response.json['id'] +
                            '/applications/1234')
        self.assertEqual(response.status_code, 404)

    def test_get_application_no_id(self):
        user_response = self.post('/users', {'name': 'steve'})
        response = self.get('/users/' + user_response.json['id'] +
                            '/applications/')
        self.assertEqual(response.status_code, 404)

    def test_get_application_no_user_id(self):
        response = self.get('/users/xx/applications/1234')
        self.assertEqual(response.status_code, 404)


class ApplicationUpdateTests(flask_test_base.FlaskTest):

    def test_update_offer(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _WEAK_APPLICATION)
        self.assertEqual(response.json['status'], 'DECLINED')
        self.assertIsNone(response.json['offer'])

        response = self.put(
            '/users/' + user_id + '/applications/' + response.json['id'],
            _STRONG_APPLICATION)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'APPROVED')

        self.assertEqual(response.json['applicant_info'], _STRONG_APPLICATION)
        self.assertIsNotNone(response.json['offer'])
        self.assertEqual(response.json['rejections'], [])

    def test_update_no_params_is_allowed(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _WEAK_APPLICATION)
        response = self.put(
            '/users/' + user_id + '/applications/' + response.json['id'], {})
        self.assertEqual(response.status_code, 200)

    def test_update_with_some_params_is_allowed(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _WEAK_APPLICATION)
        response = self.put(
            '/users/' + user_id + '/applications/' + response.json['id'], {
                'bankruptcies': 0,
                'credit_score': 1000,
                'monthly_debt': 0,
            })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json['applicant_info'], {
                'bankruptcies': 0,
                'credit_score': 1000,
                'delinquencies': 33,
                'loan_amount': 399.0,
                'monthly_debt': 0.0,
                'monthly_income': 4444444.0,
                'vehicle_value': 2000.0
            })
        self.assertIsNone(response.json['offer'])
        self.assertEqual(response.json['rejections'],
                         [{
                             'reason': 'EXCESSIVE_DELINQUENCIES'
                         }])


class ApplicationDeleteTests(flask_test_base.FlaskTest):

    def test_valid_application_delete(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _WEAK_APPLICATION)
        app_id = response.json['id']
        response = self.delete('/users/' + user_id + '/applications/' + app_id)
        self.assertEqual(response.status_code, 204)
        app = models.Application.query.get(app_id)
        self.assertIsNone(app)


class UserWithApplicationsDeleteTests(flask_test_base.FlaskTest):

    def test_valid_user_delete_with_existing_applications(self):
        response = self.post('/users', {'name': 'steve'})
        user_id = response.json['id']
        response = self.post('/users/' + user_id + '/applications',
                             _WEAK_APPLICATION)
        app_id = response.json['id']
        response = self.delete('/users/' + user_id)
        self.assertEqual(response.status_code, 204)
        user = models.User.query.get(user_id)
        self.assertIsNone(user)

        app = models.Application.query.get(app_id)
        self.assertIsNone(app)
