from swarm import Swarm, Agent
from dotenv import load_dotenv
from openai import OpenAI
import json
import textwrap

load_dotenv()

ollama = False

def get_team():
    if ollama:
        ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama"
        )

        model = "llama3.2"
        dev_model = "qwen2.5-coder:32b-base-q3_K_M"
        return Swarm(client=ollama_client), model, dev_model
    else:
        model = "gpt-4o"
        dev_model = model
        return Swarm(), model, dev_model
    
team, model, dev_model = get_team()

def print_msg(msg:dict, header:str, text: str = None):
    print("-" * 50)
    print(header)
    print("-" * 50)
    if text is not None:
        print(text)
    if msg is not None:
        print(json.dumps(msg, indent=2))
    print("=" * 50)

def transfer_to_agent_developer(instructions:str, function_template:str)->str:
    """Call this function to delegate task to DEVELOPER to implement the 'function_template' based on 'instructions'"""
    text = '''Instructions:
{0}
Function template:
{1}'''.format(textwrap.indent(instructions, '  '), textwrap.indent(function_template, '  '))
    print_msg(None,'📝 developer task 📝', text)
    return agent_developer

def transfer_to_agent_tester(test_function:str, unit_test:str)->str:
    """Call this function to delegate task to TESTER to run 'unit_test' for the 'test_function'"""
    text = '''Test function:
{0}
Unit test:
{1}'''.format(textwrap.indent(test_function, '  '), textwrap.indent(unit_test, '  '))
    print_msg(None,'⚡ tester task ⚡', text)
    return agent_tester

def transfer_to_agent_reporter(test_function:str, test_result:str)->str:
    """Call this function to delegate task to REPORTER to write REPORT using 'test_function' and 'test_result' as input"""
    text = '''Test function:
{0}
Test result:
{1}'''.format(textwrap.indent(test_function, '  '), textwrap.indent(test_result, '  '))
    print_msg(None,'✍️  reporter task ✍️', text)
    return agent_reporter

def transfer_back_to_agent_manager_from_developer(test_function:str):
    """Call this function after you complete your task to send 'test_function' to MANAGER"""
    text = '''Test function:
{0}'''.format(textwrap.indent(test_function, '  '))
    print_msg(None,'✨ developer->manager result ✨', text)
    return agent_manager

def transfer_back_to_agent_manager_from_tester(test_result:str):
    """Call this function after you complete your task to send 'test_result' to MANAGER"""
    text = '''Test result:
{0}'''.format(textwrap.indent(test_result, '  '))
    print_msg(None,'✨ tester->manager result ✨', text)
    return agent_manager

def transfer_back_to_agent_manager_from_reporter(report:str):
    """Call this function after you complete your task to send 'report' to MANAGER"""
    text = '''Report:
{0}'''.format(textwrap.indent(report, '  '))
    print_msg(None,'✨ reporter->manager result ✨', text)
    return agent_manager

def manager_instructions(context_variables:dict):
    instructions = context_variables.get("instructions")
    function_template = context_variables.get("function_template")
    unit_test = context_variables.get("unit_test")
    return f"""
    You are a manager. You do not have enough experience to execute tasks you can only delegate. Do not generate any content.
    You have 4 tasks to complete:
    1) You are responsible to delegate implementation task to DEVELOPER agent. 
       - Send him only 'instructions' ({instructions}) and 'function_template' ({function_template})
       - DO NOT send him 'unit_test'' details.
       - Expect 'test_function' as response
    2) After you receive 'test_function' from DEVELOPER you are also responsible to delegate testing task to TESTER agent
       - Send the 'test_function' and 'unit_test' ({unit_test}) to TESTER.
       - Expect PASS or FAIL 'test_result' back
    3) After you receive that information from TESTER you are also responsible to delegate reporting task to REPORTER agent
       - Send 'test_function' and 'test_status' to REPORTER agent
       - Expect written 'report' back
    4) Repond to the user with the 'report' from REPORTER, ensuring no new or inferred details are added
    """

agent_manager = Agent(
    name="MANAGER",
    model=model,
    instructions=manager_instructions,
    functions=[transfer_to_agent_developer, transfer_to_agent_tester, transfer_to_agent_reporter],
)

def developer_instructions(context_variables:dict):
    test_id = context_variables.get("test_id")
    instructions = context_variables.get("instructions")
    function_template = context_variables.get("function_template")
    unit_test = context_variables.get("unit_test")
    return f"""
You are experienced python developer.
Your sole reponsibility is to implement provided 'function_template' according to provided 'instructions'.
When you finish implementation do not test anything and always report back to MANAGER agent
by calling transfer_back_to_manager_from_developer tool passing implemented function as 'test_function'.
    """

agent_developer = Agent(
    name="DEVELOPER",
    model=dev_model,
    instructions=developer_instructions,
    functions=[transfer_back_to_agent_manager_from_developer]
)

def tester_instructions(context_variables:dict):
    test_id = context_variables.get("test_id")
    instructions = context_variables.get("instructions")
    function_template = context_variables.get("function_template")
    unit_test = context_variables.get("unit_test")
    return f"""
You are experienced python tester.
Your sole responsibility is to run provided 'unit_test' for the provided 'test_function' and nothing more.
When you finish reply back to MANAGER agent by calling transfer_back_to_manager_from_tester with PASS or FAIL 'test_status' status
    """

agent_tester = Agent(
    name="TESTER",
    model=dev_model,
    instructions=tester_instructions,
    functions=[transfer_back_to_agent_manager_from_tester]
)

def reporter_instructions(context_variables:dict):
    test_id = context_variables.get("test_id")
    instructions = context_variables.get("instructions")
    function_template = context_variables.get("function_template")
    unit_test = context_variables.get("unit_test")
    return f"""
You should receive these 2 inputs 'test_function' and 'test_result'
Fill in the following template with the given information, ensuring no new or inferred details are added. 
Only use the provided data, and maintain the format strictly as shown below:
{test_id}: 'test_result'  
'implemented_function'

When you finish reply back to MANAGER agent by calling transfer_back_to_manager_from_reporter with your 'report'
    """

agent_reporter = Agent(
    name="REPORTER",
    model=model,
    instructions=reporter_instructions,
    functions=[transfer_back_to_agent_manager_from_reporter]
)

context_variables = {
    "test_id": "TEST_1",
    "instructions": """
Implement sum() function based on the provided FUNCTION definition
""",
    "function_template": "def sum(a: int, b: int) -> int:", 
    "unit_test": """
def test_sum():
    assert sum(1, 2) == 3
    assert sum(-1, 1) == 0
    assert sum(0, 0) == 0
"""
}


task = '''Implement, test and write a report related to new function implementation'''

response = team.run(
    agent=agent_manager,
    messages=[{"role": "user", "content": task}],
    context_variables=context_variables
)

print_msg(context_variables, '👤 user 👤', task)
for msg in response.messages:
    print()
    if msg['role'] == 'assistant':
        print_msg(msg, "'🤖 assistant 🤖'")
    elif msg['role'] == 'tool':
        print_msg(msg,'⚙️  tool ⚙️')
    else:
        print_msg(msg,'? unknown ?')

text = '''Agent:
{0}
Response:
{1}'''.format(textwrap.indent(str(response.agent), '  '), textwrap.indent(str(response.messages[-1]["content"]), '  '))

print('')
print_msg(None, '🏁 result 🏁', text)