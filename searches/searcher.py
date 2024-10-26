import os
from embeddings.generate import generateEmbeddings  
from pymongo import MongoClient

from completions.completion import generateCompletion

# Function to run a vector search for job recommendations
def runVectorSearch(embeddings_deployment, AzureOpenAIClient, client, mongodb_database):
    # Clear the console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Ask the user for their query
    print("What skills and experience level do you have for job recommendations?")
    skills = input("Enter your skills: ")
    experience_level = input("Enter your experience level: ")

    # Combine skills and experience into a query
    query = f"Skills: {skills}, Experience Level: {experience_level}"

    # Define the maximum number of results and the collection name
    maxResults = 5  # Adjust as needed
    vector_column = "jobVector"  #  field where job vectors are stored
    collection_name = "jobs"  # MongoDB collection name

    # Connect to the database and the collection
    db = client[mongodb_database]
    collection = db[collection_name]

    # Perform the vector search
    results = vectorSearch(query, vector_column, collection, embeddings_deployment, AzureOpenAIClient, maxResults)

    # Print the results
    if results:
        print("\nRecommended Jobs:")
        for result in results:
            job = result['document']
            print(f"Title: {job['title']}, Description: {job['description']}, Similarity Score: {result['similarityScore']}")
    else:
        print("No recommendations found.")


def vectorSearch(query, vector_column, collection, embeddings_deployment, AzureOpenAIClient, num_results=3):
    # Generate embeddings for the query using the generateEmbeddings function from the embeddings module
    query_embedding = generateEmbeddings(query, embeddings_deployment, AzureOpenAIClient)

    # Define the pipeline for the MongoDB aggregation query
    pipeline = [
        {
            # The $search stage performs a search query on the collection
            '$search': {
                # The knn operator performs a vector search
                'knn': {
                    # The vector to search for
                    'vector': query_embedding,
                    # The path in the documents where the vector data is stored
                    'path': vector_column,
                    # The number of results to return
                    'k': num_results
                }
            }
        },
        # The $project stage includes or excludes fields from the documents
        {
            '$project': {
                # Include the similarity score in the results
                'similarityScore': {'$meta': 'searchScore'},
                # Include the original document in the results
                'document': '$$ROOT'
            }
        }
    ]
    
    # Perform the aggregation query on the collection and store the results
    results = collection.aggregate(pipeline)
    
    # Return the results as a list
    return list(results)


# Function to run a GPT search
def runGPTSearch(embeddings_deployment, AzureOpenAIClient, completion_deployment, AzureOpenAICompletionClient, client, mongodb_database):
    # Define the maximum number of results and the vector column name
    maxResults = 20
    vector_column = "jobVector"  # Adjust this based on your schema
    collection_name = "collection_name"  #  collection name

    # Connect to the database and the collection
    db = client[mongodb_database]
    collection = db[collection_name]

    # Clear the console and ask the user for their query
    user_input = ""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("What would you like to ask about the job listings? Type 'end' to end the session.")
    user_input = input("Prompt: ")

    # Keep asking for queries until the user types 'end'
    while user_input.lower() != "end":
        # Run the vector search to retrieve relevant job listings
        results_for_prompt = vectorSearch(user_input, vector_column, collection, embeddings_deployment, AzureOpenAIClient, maxResults)

        # Generate detailed insights using the completions function
        completions_results = generateCompletion(results_for_prompt, completion_deployment, AzureOpenAICompletionClient, user_input)

        # Print the completions
        print("\n" + completions_results['choices'][0]['message']['content'])

        # Ask for the next query
        print("\nWhat would you like to ask about the job listings? Type 'end' to end the session.")
        user_input = input("Prompt: ")



