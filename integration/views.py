from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import openai
from django.conf import settings

BITRIX24_WEBHOOK_URL = settings.BITRIX24_WEBHOOK_URL
CALL_API_KEY = settings.CALL_API_KEY
SUB_ACCOUNT_ID = settings.SUB_ACCOUNT_ID

@csrf_exempt
def handle_voice_call_action_webhook(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            print("Received Webhook Payload:", payload)

            session_id = payload["payload"].get("sessionId")
            recording_id = payload["payload"].get("recordingId")
            destination_number = payload["payload"].get("destination")
            last_four_digits = destination_number[-4:] if destination_number else None

            if not session_id and not recording_id:
                return JsonResponse({"error": "sessionId or recordingId is required."}, status=400)

            recording_url = fetch_recording_url(session_id, recording_id)
            if not recording_url:
                return JsonResponse({"error": "Recording not found."}, status=404)

            transcription = transcribe_recording(recording_url)
            feedback = analyze_call_feedback(transcription)

            success = upload_to_bitrix24(last_four_digits, recording_url, feedback)
            if success:
                return JsonResponse({"status": "success", "message": "Recording and feedback uploaded successfully."}, status=200)
            else:
                return JsonResponse({"error": "Failed to upload to Bitrix24."}, status=500)
        except Exception as e:
            print("Error handling webhook:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def fetch_recording_url(session_id, recording_id):
    try:
        id_to_fetch = session_id if session_id else recording_id
        url = f"https://voice.wavecell.com/api/v1/subaccounts/{SUB_ACCOUNT_ID}/recordings/{id_to_fetch}"
        headers = {"Authorization": f"Bearer {CALL_API_KEY}"}
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("url")
        else:
            print("Error fetching recording:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Exception while fetching recording:", str(e))
        return None


def transcribe_recording(recording_url):
    try:
        openai_url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}
        audio_file = requests.get(recording_url).content
        files = {"file": audio_file}
        response = requests.post(openai_url, headers=headers, files=files)

        if response.status_code == 200:
            return response.json().get("text", "No transcription available.")
        else:
            print("Error transcribing recording:", response.status_code, response.text)
            return "Error in transcription."
    except Exception as e:
        print("Exception while transcribing recording:", str(e))
        return "Error in transcription."


def analyze_call_feedback(transcription):
    try:
        openai.api_key = settings.OPENAI_API_KEY
        prompt = f"Analyze the following call transcription and provide constructive feedback: {transcription}"
        response = openai.Completion.create(
            model="text-davinci-003", prompt=prompt, max_tokens=200
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print("Exception while analyzing feedback:", str(e))
        return "Unable to generate feedback."


def upload_to_bitrix24(last_four_digits, recording_url, feedback):
    try:
        leads_response = requests.get(f"{BITRIX24_WEBHOOK_URL}crm.lead.list")
        if leads_response.status_code != 200:
            print("Error fetching leads from Bitrix24:", leads_response.text)
            return False

        leads = leads_response.json().get("result", [])
        matching_lead = None

        for lead in leads:
            phone_numbers = lead.get("PHONE", [])
            for phone in phone_numbers:
                if phone.get("VALUE", "").endswith(last_four_digits):
                    matching_lead = lead
                    break
            if matching_lead:
                break

        if not matching_lead:
            print("No matching lead found.")
            return False

        lead_id = matching_lead["ID"]
        update_data = {
            "fields": {
                "COMMENTS": f"Recording URL: {recording_url}\nFeedback: {feedback}",
            },
        }
        update_response = requests.post(
            f"{BITRIX24_WEBHOOK_URL}crm.lead.update",
            json={"id": lead_id, **update_data},
        )
        return update_response.status_code == 200
    except Exception as e:
        print("Exception while uploading to Bitrix24:", str(e))
        return False
