import sys
import os
import atexit
import numpy as np
from pathlib import Path
from collections import defaultdict
from typing import Dict
from typing_extensions import Self
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from codeplag.types import ASTFeatures, CompareInfo, FastMetrics, StructuresInfo
from codeplag.logger import codeplag_logger as logger

# from ..reporters import serialize_compare_result_to_dict, deserialize_compare_result_from_dict


HOST = "localhost"
USER = "root"
PASSWORD = "example"


class MongoDBConnection:
    def __init__(self: Self, host: str = HOST, user: str = USER, password: str = PASSWORD, db_name: str = "new_database"):
        """
        Initialization of the connection to MongoDB.

        :param host: MongoDB host.
        :param user: MongoDB username.
        :param password: MongoDB password.
        :param db_name: Database name.
        """
        self.url = self.url = f"mongodb://{user}:{password}@{host}:27017/"
        self.db_name = db_name
        self.client = None
        self.db = None

        # Connecting to MongoDB
        self.connect()

        # Registering the disconnect method for execution upon program termination
        atexit.register(self.disconnect)

    def connect(self: Self):
        """
        Connecting to MongoDB.
        """
        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')  # Checking the connection
            logger.debug("Successfully connected to MongoDB!")
            self.db = self.client[self.db_name]
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self: Self):
        """
        Disconnecting from MongoDB.
        """
        if self.client:
            self.client.close()
            logger.debug("MongoDB connection closed.")

    def get_collection(self: Self, collection_name: str):
        """
        Getting a collection by name from the current database.

        :param collection_name: Name of the collection.
        :return: Collection object of the current database.
        """

        return self.db[collection_name]


class ReportRepository:
    def __init__(self: Self, mongo_connection: MongoDBConnection):
        """
        Initialization of the repository for the compare_info collection.
        """
        self.collection = mongo_connection.get_collection("compare_info")

    def write_compare_info(
            self: Self,
            work1: ASTFeatures,
            work2: ASTFeatures,
            compare_info: CompareInfo
    ):
        """
        Insert or update a document in the compare_info collection.
        Primary key: _id (sorted paths).

        Args:
            work1 (ASTFeatures): The first file for comparison.
            work2 (ASTFeatures): The second file for comparison.
            compare_info (CompareInfo): Comparison information.
        """
        # Sorting paths to create a unique primary key
        work1, work2 = sorted([work1, work2])
        first_path, second_path = [str(work1.filepath), str(work2.filepath)]

        # Forming _id as a string of sorted paths
        document_id = {"first": first_path, "second": second_path}

        # Using the serialize_compare_result_to_dict function to convert data
        serialized_compare_info = None  # serialize_compare_result_to_dict(compare_info)

        document = {
            "_id": document_id,
            "first_path": first_path,
            "second_path": second_path,
            "first_sha256": work1.sha256,
            "second_sha256": work2.sha256,
            "first_modify_date": work1.modify_date,
            "second_modify_date": work2.modify_date,
            "compare_info": serialized_compare_info,
        }

        # Insert or update the document
        self.collection.update_one(
            {"_id": document_id},
            {"$set": document},
            upsert=True
        )
        logger.debug(f"Document for ({first_path}, {second_path}) successfully inserted/updated.")


class FeatureRepository:
    def __init__(self: Self, mongo_connection: MongoDBConnection):
        """
        Initialization of the repository for the features collection.
        """
        self.collection = mongo_connection.get_collection("features")

    def write_feature(self: Self, work: ASTFeatures, cmp_for_feature: CompareInfo):
        """
        Insert or update a document in the features collection.
        Primary key: path.

        Args:
            work (ASTFeatures): File for saving features.
            cmp_for_feature (CompareInfo): Object with required structure data.
        """
        # Forming _id as the file path
        document_id = {"first": str(work.filepath)}

        # Using the serialize_compare_result_to_dict function to convert data
        serialized_compare_info = None  # serialize_compare_result_to_dict(cmp_for_feature)

        document = {
            "_id": document_id,
            "path": document_id,
            "modify_date": work.modify_date,
            "sha256": work.sha256,
            "features": {
                "head_nodes": work.head_nodes,
                "structure": {
                    "similarity": cmp_for_feature.structure.similarity,
                    "compliance_matrix": cmp_for_feature.structure.compliance_matrix.tolist(),
                }
            },
            "compare_info": serialized_compare_info,
        }

        # Insert or update the document
        self.collection.update_one(
            {"_id": document_id},
            {"$set": document},
            upsert=True
        )
        logger.debug(f"Document for path {document_id} successfully inserted/updated.")