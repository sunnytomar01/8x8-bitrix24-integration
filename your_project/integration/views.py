from django.http import JsonResponse
from django.conf import settings
from .utils import get_8x8_call_recording, upload_file_to_bitrix24

def integrate_recordings(request):
    sub_account_id = settings.SUB_ACCOUNT_ID  
    call_api_key = settings.CALL_API_KEY 
    webhook_url = settings.BITRIX24_WEBHOOK_URL  


    session_id = request.GET.get('session_id')  
    if not session_id:
        return JsonResponse({"status": "error", "message": "Session ID is required"})

    recording_url = get_8x8_call_recording(sub_account_id, session_id, call_api_key)
    if recording_url:
       
        lead_id = request.GET.get('lead_id') 
        if not lead_id:
            return JsonResponse({"status": "error", "message": "Lead ID is required"})

        upload_response = upload_file_to_bitrix24(webhook_url, lead_id, recording_url)
        if upload_response:
            return JsonResponse({"status": "success", "message": "Recording integrated successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Failed to upload recording to Bitrix24"})
    else:
        return JsonResponse({"status": "error", "message": "No recording found"})
