from tenacity import retry, wait_random_exponential, stop_after_attempt

import time
import json

@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(10))
def generateEmbeddings(text, embeddings_deployment, AzureOpenAIClient):
    
    # Generate embeddings from the input text
    response = AzureOpenAIClient.embeddings.create(
        input=text,
        model=embeddings_deployment
    )

    # Parse the response into a json object
    embeddings = json.loads(response.model_dump_json(indent=2))

    # Small delay to avoid rate limiting (adjust if needed)
    time.sleep(0.01)

    return embeddings["data"][0]["embedding"]

def generateJobEmbedding(job, embeddings_deployment, AzureOpenAIClient):
    # Get the skills and experience level from the job data
    skills = job["skills"]
    experienceLevel = job["experience-level"]

    # Combine skills and experience level for embedding
    if skills and experienceLevel:
        textToEmbed = f"Skills: {skills}, Experience Level: {experienceLevel}"
        job["jobVector"] = generateEmbeddings(textToEmbed, embeddings_deployment, AzureOpenAIClient)

    return job