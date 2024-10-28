import os
import json
import datetime
from pymongo import UpdateOne
import models.job as Jobs
import indexing.indexer as Indexes 
import data_fetching.StoreFromCSV 
import embeddings.generate


def loadAndVectorizeJobs(client, mongodb_database, embeddings_deployment, AzureOpenAIClient, batch_size):
    # Load jobs from CSV
    jobs = data_fetching.StoreFromCSV.fetch_jobs_from_csv()
    
    
    if not jobs:
        print("No jobs found in the provided CSV.")
        return


    # Get the database and collection
    db = client[mongodb_database]
    collection_name = "jobs"  
    collection = db[collection_name]
    current_doc_idx = 0

    operations = []
    total_number_of_documents = len(jobs)
    batch_number = 1

    # Generate embeddings for each job
    for job in jobs:
        current_doc_idx += 1

        job = embeddings.generate.generateJobEmbedding(job, embeddings_deployment, AzureOpenAIClient)

         # Prepare the update operation for the document
        operations.append(UpdateOne({"_id": job["_id"]}, {"$set": job}, upsert=True))

        # Write to the collection in batches
        if len(operations) == batch_size:
            print(f"\tWriting collection {collection_name}, batch size {batch_size}, batch {batch_number}, number of documents processed so far {current_doc_idx}.")
            collection.bulk_write(operations, ordered=False)
            operations = []
            batch_number += 1

        # Print progress for every 100 documents processed
        if current_doc_idx % 100 == 0:
            print(f"\t{current_doc_idx} out of {total_number_of_documents} docs vectorized.")

    # Write any remaining operations to the collection
    if operations:
        print(f"\tWriting collection {collection_name}, batch size {batch_size}, batch {batch_number}, number of documents processed so far {current_doc_idx}.")
        collection.bulk_write(operations, ordered=False)

    print(f"(" + str(datetime.datetime.now()) + ")  " + f"Collection {collection_name}, total number of documents processed {current_doc_idx} .\n")

    # Create vector indexes for the collection
    index_list = [
        ("jobIdVectorSearchIndex", "jobIdVector"), 
        ("jobTitleVectorSearchIndex", "jobTitleVector"),
        ("roleVectorSearchIndex", "roleVector"),  
        ("jobDescriptionVectorSearchIndex", "jobDescriptionVector"),
        ("jobSkillsVectorSearchIndex", "jobSkillsVector"),
        ("experienceLevelVectorSearchIndex", "experienceLevelVector"),
        ("qualificationsVectorSearchIndex", "qualificationsVector"), 
        ("salaryRangeVectorSearchIndex", "salaryRangeVector"),
        ("locationVectorSearchIndex", "locationVector"), 
        ("countryVectorSearchIndex", "countryVector"),  
        ("latitudeVectorSearchIndex", "latitudeVector"),  
        ("longitudeVectorSearchIndex", "longitudeVector"), 
        ("workTypeVectorSearchIndex", "workTypeVector"),
        ("companySizeVectorSearchIndex", "companySizeVector"),
        ("jobPostingDateVectorSearchIndex", "jobPostingDateVector"), 
        ("preferenceVectorSearchIndex", "preferenceVector"), 
        ("contactPersonVectorSearchIndex", "contactPersonVector"),  
        ("contactVectorSearchIndex", "contactVector"), 
        ("benefitsVectorSearchIndex", "benefitsVector"),  
        ("responsibilitiesVectorSearchIndex", "responsibilitiesVector"), 
        ("companyVectorSearchIndex", "companyVector"),
        ("companyProfileVectorSearchIndex", "companyProfileVector") 
    ]

    createVectorIndexes(collection, index_list, db, collection_name)


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