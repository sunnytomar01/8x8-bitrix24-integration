import unittest
from unittest.mock import patch, MagicMock
from django.test import Client
from django.urls import reverse

class IntegrationTestCase(unittest.TestCase):

    @patch('your_app.views.get_8x8_call_recording')
    @patch('your_app.views.get_new_recordings')
    @patch('your_app.views.upload_file_to_bitrix24')
    @patch('your_app.views.transcribe_audio')
    @patch('your_app.views.analyze_call_feedback')
    @patch('your_app.views.get_bitrix24_lead_id_by_phone')
    def test_integration(self, mock_get_bitrix24_lead_id_by_phone, mock_analyze_call_feedback,
                          mock_transcribe_audio, mock_upload_file_to_bitrix24, mock_get_new_recordings, 
                          mock_get_8x8_call_recording):
        # Set up mock return values for the 8x8 API and Bitrix24 API interactions
        
        # Mock response for getting 8x8 call recordings
        mock_get_8x8_call_recording.return_value = {
            'url': 'https://example.com/recording.mp3',
            'other_party': '+1234567890'
        }
        
        # Mock response for getting new 8x8 recordings
        mock_get_new_recordings.return_value = [
            {'id': 'rec_123', 'other_party': '+1234567890', 'url': 'https://example.com/recording.mp3'}
        ]
        
        # Mock response for getting Bitrix24 lead by phone number (last 4 digits match)
        mock_get_bitrix24_lead_id_by_phone.return_value = 'lead_123'
        
        # Mock response for transcribing audio (e.g., from OpenAI API)
        mock_transcribe_audio.return_value = "This is the transcription of the call."
        
        # Mock response for analyzing the call feedback
        mock_analyze_call_feedback.return_value = "The call was good, but could improve the closing."

        # Mock response for uploading a file to Bitrix24
        mock_upload_file_to_bitrix24.return_value = {'status': 'success'}

        # Create a test client to simulate a request to the Django view
        client = Client()

        # Test the `check_new_recordings` view (replace 'check_new_recordings' with the correct URL name)
        response = client.get(reverse('check_new_recordings'))  # Replace with the correct URL name
        self.assertEqual(response.status_code, 200)
        self.assertIn('New recordings processed', response.content.decode())

        # Test the `integrate_recordings` view with a recording_id (mocked for this test)
        response = client.get(reverse('integrate_recordings'), {'recording_id': 'rec_123'})  # Replace with correct URL name
        self.assertEqual(response.status_code, 200)
        self.assertIn('Recording integrated successfully', response.content.decode())

        # Additional assertion to ensure feedback was uploaded to Bitrix24
        mock_upload_file_to_bitrix24.assert_called_with(
            'https://example.com/recording.mp3', 'lead_123', 'This is the transcription of the call.'
        )

# Ensure this code runs as part of the test suite
if __name__ == '__main__':
    unittest.main()
