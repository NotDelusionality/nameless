import unittest
import json
from unittest.mock import patch, MagicMock
from app import app

class ChatbotTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_health_check(self):
        response = self.app.get('/health')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'ok')

    def test_chat_no_messages(self):
        response = self.app.post('/chat',
                                 data=json.dumps({}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'No messages provided')

    @patch('app.client')
    def test_chat_success(self, mock_client):
        # Mock the client and its nested methods
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello! How can I help you?"
        mock_client.chat.completions.create.return_value = mock_response

        response = self.app.post('/chat',
                                 data=json.dumps({"messages": [{"role": "user", "content": "hi"}]}),
                                 content_type='application/json')

        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['reply'], "Hello! How can I help you?")

    @patch('app.client', None)
    def test_chat_no_api_key(self):
        response = self.app.post('/chat',
                                 data=json.dumps({"messages": [{"role": "user", "content": "hi"}]}),
                                 content_type='application/json')
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(data['error'], 'OpenAI API key not configured')

if __name__ == '__main__':
    unittest.main()
