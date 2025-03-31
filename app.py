import falcon
import os
import subprocess
import tempfile
import json
from falcon_multipart.middleware import MultipartMiddleware
## Handy command to run the program python3 -m gunicorn -b 0.0.0.0:4646 app:app

from llmutils import build_answer_extraction_message, build_code_query_message
from llmcaller import call_llm

class ReuqestHandler:

    def on_post(self, req, resp):
        question = req.get_param('question')
        if not question:
            resp.status = falcon.HTTP_400
            resp.media = {
                'error': 'You must provide a question/task to perform'
            }
            return
        current_directory = os.getcwd()
        filenames_constraint = []
        uploaded_file_paths = []
        uploaded_files = req.get_param('files', default=[])
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]

        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                file_name = uploaded_file.filename
                file_path = os.path.join(current_directory, file_name)
                filenames_constraint.append(file_name)
                with open(file_path, 'wb') as file:
                    file.write(uploaded_file.file.read())
                uploaded_file_paths.append(file_path)
        try:
            answer = process_user_query(question, filenames_constraint)
            resp.media = {
                'answer': answer
            }
        except Exception as e:
            resp.media = {
                'error': 'Something went wrong'
            }
        finally:
            for _uploaded_file_path in uploaded_file_paths:
                os.remove(_uploaded_file_path)


def code_executor(code: str, arguments: dict = None):
    current_directory = os.getcwd()
    with tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w', dir=current_directory) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    execution_info = {
        'execution_status': False,
        'standard_output': None,
        'error': None,
    } 
    try:
        argument_list = ['python3', temp_file_path]
        if arguments:
            for key, value in arguments:
                argument_list.append(f'--{key}')
                argument_list.append(value)
        result = subprocess.run(argument_list, check=True, stdout=subprocess.PIPE, cwd=current_directory)
        execution_info['execution_status'] = True
        execution_info['standard_output'] = result.stdout.decode()
    except Exception as e:
        execution_info['error'] = str(e)
    finally:
        os.remove(temp_file_path)
    return execution_info


def process_user_query(user_question: str, filenames: list = None):
    messages = [
        {
            'role': 'user',
            'content': build_code_query_message(user_question, filenames)
        }
    ]
    code_query_response = call_llm(messages)
    json_code_query_response = json.loads(code_query_response)
    if not json_code_query_response.get('code'):
        return json_code_query_response['answer']
    messages.append({
        'role': 'assistant',
        'content': code_query_response
    })
    code_execution_result_info = code_executor(json_code_query_response['code'])
    messages.append({
        'role': 'user',
        'content': build_answer_extraction_message(code_execution_result_info['standard_output'])
    })
    answer_extraction = call_llm(messages)
    json_answer_extraction = json.loads(answer_extraction)
    return json_answer_extraction['answer']

app = falcon.App(middleware=[MultipartMiddleware()])

request_handler = ReuqestHandler()

app.add_route('/', request_handler)
