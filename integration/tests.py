from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
import json

class IntegrationTestCase(TestCase):

    @patch('integration.views.get_8x8_call_recording')
    @patch('integration.views.transcribe_audio')
    @patch('integration.views.analyze_call_feedback')
    @patch('integration.views.upload_file_to_bitrix24')
    def test_integrate_recordings_success(self, mock_upload, mock_analyze, mock_transcribe, mock_get_recording):
        # Setup mock return values
        mock_get_recording.return_value = "http://example.com/recording.mp3"
        mock_transcribe.return_value = "This is the transcribed text of the call."
        mock_analyze.return_value = "Feedback: Improve closing statements."
        
        # Simulate a successful upload response
        mock_upload.return_value = {
            'status': 'success',
            'message': 'File uploaded successfully'
        }

        # Simulate a GET request with session_id and lead_id
        response = self.client.get(reverse('integrate_recordings'), {'session_id': '12345', 'lead_id': '54321'})

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Check the JSON response content
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'success')
        self.assertIn('Recording integrated successfully', response_json['message'])
        self.assertIn('Feedback:', response_json['feedback'])

    @patch('integration.views.get_8x8_call_recording')
    def test_integrate_recordings_no_session_id(self, mock_get_recording):
        # Simulate a GET request with no session_id
        response = self.client.get(reverse('integrate_recordings'), {'lead_id': '54321'})

        # Check if the response returns the correct error message
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Session ID is required')

    @patch('integration.views.get_8x8_call_recording')
    def test_integrate_recordings_no_lead_id(self, mock_get_recording):
        # Simulate a GET request with no lead_id
        response = self.client.get(reverse('integrate_recordings'), {'session_id': '12345'})

        # Check if the response returns the correct error message
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Lead ID is required')

    @patch('integration.views.get_8x8_call_recording')
    def test_integrate_recordings_no_recording_found(self, mock_get_recording):
        # Simulate a GET request where no recording is found
        mock_get_recording.return_value = None
        response = self.client.get(reverse('integrate_recordings'), {'session_id': '12345', 'lead_id': '54321'})

        # Check if the response returns the correct error message
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'No recording found')

    @patch('integration.views.get_8x8_call_recording')
    @patch('integration.views.transcribe_audio')
    def test_integrate_recordings_transcription_failed(self, mock_transcribe, mock_get_recording):
        # Simulate a transcription failure
        mock_get_recording.return_value = "http://example.com/recording.mp3"
        mock_transcribe.return_value = None

        response = self.client.get(reverse('integrate_recordings'), {'session_id': '12345', 'lead_id': '54321'})

        # Check if the response returns the correct error message
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Failed to transcribe the recording')

    @patch('integration.views.get_8x8_call_recording')
    @patch('integration.views.upload_file_to_bitrix24')
    def test_integrate_recordings_upload_failed(self, mock_upload, mock_get_recording):
        # Simulate a failed upload to Bitrix24
        mock_get_recording.return_value = "http://example.com/recording.mp3"
        mock_upload.return_value = None  # Simulate that upload failed

        # Simulate a GET request with session_id and lead_id
        response = self.client.get(reverse('integrate_recordings'), {'session_id': '12345', 'lead_id': '54321'})

        # Check if the response returns the correct error message
        response_json = json.loads(response.content)
        self.assertEqual(response_json['status'], 'error')
        self.assertEqual(response_json['message'], 'Failed to upload recording to Bitrix24')
