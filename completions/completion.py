import json
from openai import AzureOpenAI

# Function to generate completions for a given prompt
def generateCompletion(prompt, completion_deployment, AzureOpenAICompletionClient, user_input):
    # Define the system prompt
    system_prompt = '''
    You are an intelligent assistant for the Job Listing System.
    You are designed to provide helpful answers to user questions about the job listings given the information provided.
        - Only answer questions related to the information provided below, provide 3 clear suggestions in a list format.
        - Write two lines of whitespace between each answer in the list.
        - Only provide answers that relate to the job listings available.
        - If you're unsure of an answer, you can say "I don't know" or "I'm not sure" and recommend users search themselves."
    '''

    # Initialize the messages list with the system prompt and user input
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    
    # Add each item in the prompt to the messages list
    for item in prompt:
        messages.append({"role": "system", "content": item['document']['categoryName'] + " " + item['document']['name']})
    
    # Generate the chat completions using the AzureOpenAICompletionClient
    response = AzureOpenAICompletionClient.chat.completions.create(model=completion_deployment, messages=messages)
    
    # Parse the response into a JSON object
    completions = json.loads(response.model_dump_json(indent=2))

    # Return the completions
    return completions
