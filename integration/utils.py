import requests
import openai


def fetch_recording_url(sub_account_id, session_id, recording_id, api_key):
    """
    Fetch the recording URL from 8x8 using session_id or recording_id.
    """
    try:
        id_to_fetch = session_id if session_id else recording_id
        url = f"https://voice.wavecell.com/api/v1/subaccounts/{sub_account_id}/recordings/{id_to_fetch}"
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            recording_data = response.json()
            return recording_data.get("url")
        else:
            print("Error fetching recording:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Exception while fetching recording:", str(e))
        return None


def transcribe_recording(recording_url, openai_api_key):
    """
    Transcribe the call recording using OpenAI's Whisper API.
    """
    try:
        openai_url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {openai_api_key}"}
        audio_file = requests.get(recording_url).content
        files = {"file": ("audio.mp3", audio_file)}

        response = requests.post(openai_url, headers=headers, files=files)
        if response.status_code == 200:
            transcription_data = response.json()
            return transcription_data.get("text", "No transcription available.")
        else:
            print("Error transcribing recording:", response.status_code, response.text)
            return "Error in transcription."
    except Exception as e:
        print("Exception while transcribing recording:", str(e))
        return "Error in transcription."


def analyze_call_feedback(transcription, openai_api_key):
    """
    Analyze the transcription and generate feedback using OpenAI GPT.
    """
    try:
        openai.api_key = openai_api_key
        prompt = f"Analyze the following call transcription and provide constructive feedback: {transcription}"
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print("Exception while analyzing feedback:", str(e))
        return "Unable to generate feedback."


def fetch_leads_from_bitrix24(webhook_url):
    """
    Fetch all leads from Bitrix24.
    """
    try:
        response = requests.get(f"{webhook_url}crm.lead.list")
        if response.status_code == 200:
            return response.json().get("result", [])
        else:
            print("Error fetching leads from Bitrix24:", response.text)
            return []
    except Exception as e:
        print("Error fetching leads:", str(e))
        return []


def match_lead_by_phone(leads, last_four_digits):
    """
    Match a lead based on the last four digits of the phone number.
    """
    for lead in leads:
        phone_numbers = lead.get("PHONE", [])
        for phone in phone_numbers:
            if phone.get("VALUE", "").endswith(last_four_digits):
                return lead
    return None


def upload_to_bitrix24(webhook_url, lead_id, recording_url, feedback):
    """
    Upload the recording and feedback to the specified lead in Bitrix24.
    """
    try:
        update_data = {
            "fields": {
                "COMMENTS": f"Recording URL: {recording_url}\nFeedback: {feedback}",
            },
        }
        response = requests.post(
            f"{webhook_url}crm.lead.update",
            json={"id": lead_id, **update_data},
        )
        return response.status_code == 200
    except Exception as e:
        print("Error uploading to Bitrix24:", str(e))
        return False
