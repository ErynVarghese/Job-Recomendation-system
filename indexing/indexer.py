import os
import json
import datetime
from pymongo import UpdateOne
import models.job as Jobs  #  job model 
import indexing.indexer as Indexes  #  index creation logic 

# load and vectorize local job data to MongoDB cluster
def loadAndVectorizeLocalBlobDataToMongoDBCluster(client, data_folder, mongodb_database, batch_size, embeddings_deployment, AzureOpenAIClient, process_jobs_vector):
    # Get list of files in the data folder
    local_blobs_files = os.listdir(data_folder)

    # Iterate over each file in the folder
    for blob_file in local_blobs_files:
        batch_number = 1

        # Process only JSON files
        if blob_file.endswith(".json"):
            print("\n(" + str(datetime.datetime.now()) + ")  " + blob_file)

            # Open the file and load its content
            with open(os.path.join(data_folder, blob_file), 'r') as file:
                json_data = json.load(file)

           
            total_number_of_documents = len(json_data)

            if total_number_of_documents >= 0:
                # Get the collection name from the file name 
                collection_name = blob_file.split(".json")[0]

                # Get the database and collection
                db = client[mongodb_database]
                collection = db[collection_name]
                current_doc_idx = 0

                operations = []

                # Iterate over each document in the JSON data
                for doc in json_data:
                    current_doc_idx += 1

                    # Generate embeddings for the job data based on skills and experience level
                    if collection_name == "jobs" and process_jobs_vector:
                        doc = Jobs.generateJobEmbedding(doc, embeddings_deployment, AzureOpenAIClient)

                   
                    if current_doc_idx % 100 == 0 and process_jobs_vector:
                        print(f"\t{current_doc_idx} out of {total_number_of_documents} docs vectorized.")

                    # Prepare the update operation for the document
                    operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": doc}, upsert=True))

                    # Write to the collection in batches
                    if len(operations) == batch_size:
                        print(f"\tWriting collection {collection_name}, batch size {batch_size}, batch {batch_number}, number of documents processed so far {current_doc_idx}.")
                        collection.bulk_write(operations, ordered=False)
                        operations = []
                        batch_number += 1

                # Write any remaining operations to the collection
                if len(operations) > 0:
                    print(f"\tWriting collection {collection_name}, batch size {batch_size}, batch {batch_number}, number of documents processed so far {current_doc_idx}.")
                    collection.bulk_write(operations, ordered=False)

                print(f"({str(datetime.datetime.now())})  Collection {collection_name}, total number of documents processed {current_doc_idx}.\n")

                # Create the vector indexes for the jobs collection based on the job vector (skills and experience level)
                if process_jobs_vector and collection_name == "jobs":
                    index_list = [("jobVectorSearchIndex", "jobVector")]  # Adjusted for the new context
                    Indexes.createVectorIndexes(collection, index_list, db, collection_name)


# Function to create vector indexes in a MongoDB collection
def createVectorIndexes(collection, index_list, db, collection_name):
    # Get information about the existing indexes in the collection
    collection_indexes = collection.index_information()

    # Iterate over each index in the index_list
    for indexname, vectorColumn in index_list:
        
        # Check if the index already exists, and drop it if necessary
        if indexname in collection_indexes:
            collection.drop_index(indexname)

        # Create a new IVF index in the collection
        db.command({
            'createIndexes': collection_name,
            'indexes': [
                {
                    'name': indexname,
                    'key': {
                        f"{vectorColumn}": "cosmosSearch"
                    },
                    'cosmosSearchOptions': {
                        'kind': 'vector-ivf',
                        'numLists': 1,
                        'similarity': 'COS',  # Cosine similarity
                        'dimensions': 1536  #  embedding dimension 
                    }
                }
            ]
        })