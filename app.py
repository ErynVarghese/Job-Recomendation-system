# Import necessary modules and functions
import embeddings.generate as Embeddings
import indexing.indexer as Indexer
import searches.searcher as Searcher
import data_fetching.StoreFromCSV  # Import the StoreFromCSV module

import os
import pymongo
from dotenv import load_dotenv
from openai import AzureOpenAI 

def main():
    # Load environment variables
    load_dotenv(".env")
    
    # Retrieve environment variables
    cosmosdb_connection_string = os.getenv('COSMOSDB_ENDPOINT')
    mongodb_database = os.getenv('COSMOSDB_DATABASE')
    azure_endpoint = os.getenv('OPENAI_ENDPOINT')
    api_key = os.getenv('OPENAI_KEY')
    embeddings_deployment = os.getenv('EMBEDDINGS_DEPLOYMENT')
    completion_deployment = os.getenv('COMPLETION_DEPLOYMENT')

   
    AzureOpenAIClient = AzureOpenAI(azure_endpoint, api_key, embeddings_deployment)
    AzureOpenAICompletionClient = AzureOpenAI(azure_endpoint, api_key, completion_deployment)
    
    # Set up MongoDB connection
    client = pymongo.MongoClient(cosmosdb_connection_string)

    while True:
        print("Choose an option:")
        print("1. Load jobs from CSV, store in MongoDB, and create vector index")  # Combined option
        print("2. Vector search")
        print("3. GPT-based search")
        print("0. Exit")
        
        choice = input("Option: ")

        if choice == "1":
            # Load jobs from CSV, store in MongoDB, and create vector index
            csv_file_path = input("Enter the path to the CSV file: ")
            jobs = data_fetching.StoreFromCSV.fetch_jobs_from_csv(csv_file_path) 
            
            if jobs:
                data_fetching.StoreFromCSV.store_jobs_in_mongodb(jobs, client, mongodb_database)  
                print(f"Stored {len(jobs)} jobs in MongoDB from CSV.")
                
                
                Indexer.createVectorIndex(client, mongodb_database)  
                
            else:
                print("No jobs found in the provided CSV.")
        
        elif choice == "2":
            # Run vector search
            Searcher.runVectorSearch(embeddings_deployment, AzureOpenAIClient, client, mongodb_database)
        
        elif choice == "3":
            # Run GPT search
            Searcher.runGPTSearch(
                embeddings_deployment, AzureOpenAIClient, completion_deployment, AzureOpenAICompletionClient,
                client, mongodb_database)
        
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
