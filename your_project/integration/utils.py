import requests


def get_8x8_call_recording(sub_account_id, session_id, api_key):
    url = f"https://voice.wavecell.com/api/v1/subaccounts/{sub_account_id}/recordings/{session_id}"
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            data = response.json()
            if 'data' in data and data['data']:
               
                return data['data'][0]['url']
            else:
                print("No recording found for session_id:", session_id)
                return None
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print(f"Error fetching recording: {response.status_code} - {response.text}")
        return None


def upload_file_to_bitrix24(webhook_url, lead_id, file_url):
    file_data = {
        'file': ('file.mp3', requests.get(file_url).content, 'audio/mpeg')
    }

    file_upload_url = f'{webhook_url}/crm.lead.uploadfile.json'
    response = requests.post(file_upload_url, files=file_data)

    if response.status_code == 200:
        file_info = response.json()
        file_id = file_info.get('file_id')

        data = {
            'id': lead_id,
            'FIELDS': {
                'FILE': file_id  
            }
        }
        update_response = requests.post(f'{webhook_url}/crm.lead.update.json', json=data)
        return update_response.json()
    else:
        return None
