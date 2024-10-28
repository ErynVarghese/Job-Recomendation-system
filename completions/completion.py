import json
from openai import AzureOpenAI

# Function to generate completions for job search
def generateCompletion(prompt, completion_deployment, AzureOpenAICompletionClient, user_input):
    system_prompt = '''
    You are an assistant specializing in job recommendations. Based on the provided data, suggest relevant job matches.
    - Provide three suitable job options with brief details.
    - Space each suggestion with two lines.
    - Respond "I'm not sure" if the data doesn't match user needs.
    '''

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input},
    ]
    
    for item in prompt:
        messages.append({"role": "system", "content": f"{item['document']['title']} at {item['document']['company']} in {item['document']['location']} with {item['document']['experience_level']} experience"})

    response = AzureOpenAICompletionClient.chat.completions.create(model=completion_deployment, messages=messages)
    completions = json.loads(response.model_dump_json(indent=2))

    return completions