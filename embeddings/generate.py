import time
import json
import os
from openai import OpenAI
import asyncio

# API key
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=api_key)

async def generate_job_embedding(job_data, embeddings_deployment):
    # Concatenating skills and job title
    job_name = f"Skills - {job_data['skills']}, Job Title - {job_data['job_title']}"

    if job_name:
        job_data["jobVector"] = await generate_embeddings(job_name, embeddings_deployment)

    return job_data

async def generate_embeddings(text, embeddings_deployment):
    # Generate embeddings from the string of text
    try:
        response = await asyncio.to_thread(openai_client.create_embedding,  
                                            model=embeddings_deployment,
                                            input=text)


        embeddings = response['data'][0]['embedding']  

        # Avoid rate limiting
        await asyncio.sleep(0.01)  

        return embeddings

    except Exception as e:
        print(f"Error generating embeddings: {e}")
        return None  