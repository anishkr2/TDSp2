import requests
import json
api_key = 'eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDEwODhAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.riAG634O2tYMFs2TiLxJ89TpCA6sr00BYlKF4HVIA0I'
api_url = 'https://aiproxy.sanand.workers.dev/openai/v1/chat/completions'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}
from llmutils import build_code_query_message

def call_llm(messages: list):
    data = {
        'model': 'gpt-4o-mini',
        'messages': messages,
        'temperature': 0,
        'response_format': {
            'type': 'json_object'
        }
    }
    response = requests.post(api_url, headers=headers, data=json.dumps(data))
    structured_response = response.json()
    return structured_response['choices'][0]['message']['content']
