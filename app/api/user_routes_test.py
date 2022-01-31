# TODO DO NOT SUBMIT
from testing import flask_test_base
import json


class UserCreationTests(flask_test_base.FlaskTest):

    def test_create_user(self):
        response = self.post('/users', {'name': 'steve'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json['applications'], [])
        self.assertEqual(response.json['name'], 'steve')

    def test_create_user_empty_name_is_rejected(self):
        response = self.post('/users', {'name': ''})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json, {
                'data': {
                    'name': ''
                },
                'messages': {
                    'name': ["Shorter than minimum length 1."]
                },
                'status': 422,
                'title': 'One or more parameters did not validate.',
                'valid_data': {}
            })

    def test_create_user_no_name_is_rejected(self):
        response = self.post('/users', {})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json, {
                'data': {},
                'messages': {
                    'name': ["Missing data for required field 'name'."]
                },
                'status': 422,
                'title': 'One or more parameters did not validate.',
                'valid_data': {}
            })


class UserGetTests(flask_test_base.FlaskTest):

    def test_get_valid_user(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.get('/users/' + response.json['id'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['applications'], [])
        self.assertEqual(response.json['name'], 'steve')

    def test_get_invalid_user(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.get('/users/xajk3')
        self.assertEqual(response.status_code, 404)

    def test_get_user_no_id(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.get('/users/')
        self.assertEqual(response.status_code, 404)


class UserUpdateTests(flask_test_base.FlaskTest):

    def test_valid_user_update(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.put('/users/' + response.json['id'],
                            {'name': 'jimbob'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['applications'], [])
        self.assertEqual(response.json['name'], 'jimbob')

    def test_valid_empty_user_update(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.put('/users/' + response.json['id'], {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['applications'], [])
        self.assertEqual(response.json['name'], 'steve')

    def test_valid_user_invalid_update(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.put('/users/' + response.json['id'], {
            'name': 'jimbob',
            'foo': 'bar'
        })

        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.json, {
                'data': {
                    'foo': 'bar',
                    'name': 'jimbob'
                },
                'messages': {
                    'foo': ["Unknown field."]
                },
                'status': 422,
                'title': 'One or more parameters did not validate.',
                'valid_data': {
                    'name': 'jimbob'
                }
            })

    def test_invalid_user_valid_update(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.put('/users/12345', {'name': 'jimbob'})
        self.assertEqual(response.status_code, 404)

    def test_invalid_user_invalid_update(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.put('/users/12345', {'name': 'jimbob', 'foo': 'bar'})
        self.assertEqual(response.status_code, 404)


class UserDeleteTests(flask_test_base.FlaskTest):

    def test_valid_user_delete(self):
        response = self.post('/users', {'name': 'steve'})
        response = self.delete('/users/' + response.json['id'])
        self.assertEqual(response.status_code, 204)
