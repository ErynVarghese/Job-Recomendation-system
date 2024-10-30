import os
from embeddings.generate import generateEmbeddings  
from pymongo import MongoClient

import completions.completion
import embeddings.generate

from completions.completion import generateCompletion

# Function to run a vector search for jobs
def runJobVectorSearch(embeddings_deployment, AzureOpenAIClient, client, mongodb_database):
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Ask the user for their query
    print("What type of job are you looking for?")
    user_input = input("Enter job-related query: ")
    
    # Define max results, vector column name, and collection name for jobs
    maxResults = 20
    vector_column = "jobVector"
    collection_name = "jobs"

    # Connect to the database and the collection
    db = client[mongodb_database]
    collection = db[collection_name]
    
    # Run the vector search and print the results
    results = vectorSearch(user_input, vector_column, collection, embeddings_deployment, AzureOpenAIClient, maxResults)
    for result in results:
        print(f"Similarity Score: {result['similarityScore']}"
              + f", Job Title: {result['document']['title']}" 
              + f", Company: {result['document']['company']}"
              + f", Location: {result['document']['location']}"
              + f", Experience Level: {result['document']['experience_level']}")
  
# Function to run a GPT search for jobs
def runJobGPTSearch(embeddings_deployment, AzureOpenAIClient, completion_deployment, AzureOpenAICompletionClient, client, mongodb_database):
    maxResults = 20
    vector_column = "jobVector"
    collection_name = "jobs"

    db = client[mongodb_database]
    collection = db[collection_name]

    os.system('cls' if os.name == 'nt' else 'clear')
    print("Enter a query to explore job opportunities (or type 'end' to quit):")
    user_input = input("Query: ")
    
    while user_input.lower() != "end":
        results_for_prompt = vectorSearch(user_input, vector_column, collection, embeddings_deployment, AzureOpenAIClient, maxResults)
        completions_results = generateCompletion(results_for_prompt, completion_deployment, AzureOpenAICompletionClient, user_input)
        
        print("\n"+completions_results['choices'][0]['message']['content'])
        print("\nEnter another query or type 'end' to quit.")
        user_input = input("Query: ")


# vectorSearch function for job fields
def vectorSearch(query, vector_column, collection, embeddings_deployment, AzureOpenAIClient, num_results=3):
    query_embedding = embeddings.generate.generateEmbeddings(query, embeddings_deployment, AzureOpenAIClient)

# Define the pipeline for the MongoDB aggregation query
    pipeline = [
    {
        # The $search stage performs a search query on the collection
        '$search': {
            # The cosmosSearch operator performs a vector search
            "cosmosSearch": {
                # The vector to search for
                "vector": query_embedding,
                # The path in the documents where the vector data is stored
                "path": vector_column,
                # The number of results to return
                "k": num_results
            },
            # Return the original document in the results
            "returnStoredSource": True
        }
    },
    # The $project stage includes or excludes fields from the documents
    {'$project': { 
        # Include the similarity score in the results
        'similarityScore': { '$meta': 'searchScore' }, 
        # Include the original document in the results
        'document': '$$ROOT' 
    }}
]

    # Perform the aggregation query on the collection and store the results
    results = collection.aggregate(pipeline)
    # Return the results
    return results




   
