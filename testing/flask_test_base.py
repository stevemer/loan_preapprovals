import unittest
from tenet import create_app, db
import json

class FlaskTest(unittest.TestCase):

    def get_api_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def setUp(self):
        self.maxDiff = None
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def post(self, route, data):
        return self.client.post(route, headers=self.get_api_headers(), data=json.dumps(data))

    def get(self, route):
        return self.client.get(route, headers=self.get_api_headers())

    def put(self, route, data):
        return self.client.put(route, headers=self.get_api_headers(), data=json.dumps(data))

    def delete(self, route):
        return self.client.delete(route, headers=self.get_api_headers())
