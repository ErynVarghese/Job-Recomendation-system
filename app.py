# Import necessary modules and functions
import embeddings.generate as Embeddings
import indexing.indexer as Indexer
import searches.searcher as Searcher
import data_fetching.StoreFromCSV  

from config import COSMOSDB_ENDPOINT,COSMOSDB_DATABASE,OPENAI_ENDPOINT,OPENAI_KEY,EMBEDDINGS_DEPLOYMENT,COMPLETION_DEPLOYMENT

import os
import pymongo
from dotenv import load_dotenv
from openai import AzureOpenAI 

def main():
    # Load environment variables
    load_dotenv(".env")
    batch_size = 1000



        # Create AzureOpenAI client for embeddings
    AzureOpenAIClient = AzureOpenAI(
            azure_endpoint = OPENAI_ENDPOINT
            , api_key = OPENAI_KEY
            , api_version = "2023-05-01"
            , azure_deployment = EMBEDDINGS_DEPLOYMENT
    )

        # Create AzureOpenAI client for completion
    AzureOpenAICompletionClient = AzureOpenAI(
            azure_endpoint = OPENAI_ENDPOINT
            , api_key = OPENAI_KEY
            , api_version = "2023-05-01"
            , azure_deployment = COMPLETION_DEPLOYMENT
    )
    

    
    # Set up MongoDB connection
    client = pymongo.MongoClient(COSMOSDB_ENDPOINT)

    while True:
        print("Choose an option:")
        print("1. Load jobs from CSV, store in MongoDB, and create vector index") 
        print("2. Vector search")
        print("3. GPT-based search")
        print("0. Exit")
        
        choice = input("Option: ")

        if choice == "1":
            # Load jobs from CSV, store in MongoDB, and create vector index
           
 
            Indexer.loadAndVectorizeJobs(client, COSMOSDB_DATABASE, EMBEDDINGS_DEPLOYMENT, AzureOpenAIClient, batch_size)
        
        elif choice == "2":
            # Run vector search
            Searcher.runJobVectorSearch(EMBEDDINGS_DEPLOYMENT, AzureOpenAIClient, client, COSMOSDB_DATABASE)
        
        elif choice == "3":
            # Run GPT search
            Searcher.runJobGPTSearch(
                EMBEDDINGS_DEPLOYMENT, AzureOpenAIClient, COMPLETION_DEPLOYMENT, AzureOpenAICompletionClient,
                client, COSMOSDB_DATABASE)
        
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
