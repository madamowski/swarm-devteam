import requests

dev_model = "qwen2.5-coder:7b-base-q3_K_M"

def print_msg(msg:dict, header:str, text: str = None):
    print("-" * 50)
    print(header)
    print("-" * 50)
    if text is not None:
        print(text)
    if msg is not None:
        print(json.dumps(msg, indent=2))
    print("=" * 50)

def ask_to_code(prompt: str) -> str:
   try:
       
        full_prompt = prompt + """
Do not run code. Do not provide example usage. Do not explain anything. Do not write any comments.
Return only what you are being asked for and nothing more.
"""
        print_msg(None, f"👨‍💻 DEVELOPER (model:{dev_model} input) 👨‍💻", full_prompt)

        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': dev_model,
                'prompt': full_prompt,
                'stream': False
            },
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()  # Raise exception for bad status codes
        
        result = response.json()

        print_msg(None, "👨‍💻 DEVELOPER (model:{dev_model} output) 👨‍💻", result['response'])

        return result['response']
       
   except requests.exceptions.RequestException as e:
       print(f"Error calling Ollama API: {e}")
       raise

#Complete sum() function implementation in python based on the provided function signature. 

# Example usage
if __name__ == "__main__":
   try:
       question = """
Implement sum() function based on the provided function signature. 
```
def sum(a: int, b: int) -> int:
```
"""
       answer = ask_to_code(question)
       print(f"Question: {question}")
       print(f"Answer: {answer}")
       
   except Exception as e:
       print(f"Failed to get response: {e}")