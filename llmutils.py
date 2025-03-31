message_for_code_request = """
You are an AI assistant designed to solve problems who always return the output in json format. Depending on the problem's complexity, you must decide whether to provide a direct answer or generate code that needs execution to obtain the answer.If the problem can be solved without execution, return an answer. If execution is required (e.g., for file operations, calculations, or data processing), return a code that should be executed. Do not include an answer in this case.
File Constraints:
The user will provide a list of available file names. If the task involves file operations, you must strictly refer only to these files. Do not assume the existence of any other files. If a necessary file is missing, indicate the issue instead of proceeding with assumptions.
No Clarifications Rule:
You cannot ask the user for additional clarifications. Work only with the information given. If any detail is missing, make an intelligent assumption and proceed accordingly.

Always clearly differentiate between code and answer. Ensure that code is executable and does not contain syntax errors if there are not code return an empty string. The output of the code should be printed and structured for easy answer extraction.
"""


message_for_answer_extraction = """
The provided code was successfully executed, and the raw output is available. Your task is to extract and format the final answer based on the execution output.
Identify the relevant information from the output that constitutes the final answer.
If multiple values exist, return only the most relevant one.
Present the answer in a concise and human-readable format without additional commentary.
Return only the answer, without explanations or extra details in json format. Strictly adhere to the answer no need for explanation or anything else.
For example - extracting the answer in 'Value of 2+2 is 4' will be '4'
"""


def build_code_query_message(user_question: str, filenames: list = None):
    _filenames = ''
    if filenames:
        _filenames = ",".join(filenames)
    _user_question = f'\nProblem: {user_question}'
    file_constraints = f'\nFile Constraints: {_filenames}'
    final_query = message_for_code_request + _user_question + file_constraints
    return final_query


def build_answer_extraction_message(code_execution_output: str):
    _output = f'\nCode Execution Output: {code_execution_output}'
    return message_for_answer_extraction + _output
