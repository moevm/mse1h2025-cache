import atexit

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from typing_extensions import Self

from codeplag.consts import DEFAULT_MONGO_HOST, DEFAULT_MONGO_PASS, DEFAULT_MONGO_USER
from codeplag.featurescache import AbstractFeaturesCache, serialize_features_to_dict
from codeplag.logger import codeplag_logger as logger
from codeplag.reporters import AbstractReporter, serialize_compare_result_to_dict
from codeplag.types import ASTFeatures, CompareInfo

HOST = DEFAULT_MONGO_HOST
USER = DEFAULT_MONGO_USER
PASSWORD = DEFAULT_MONGO_PASS


class MongoDBConnection:
    def __init__(
        self: Self,
        host: str = HOST,
        user: str = USER,
        password: str = PASSWORD,
        db_name: str = "new_database",
    ) -> None:
        """Initialize the connection to MongoDB.

        Args:
            host (str): MongoDB host address.
            user (str): MongoDB username for authentication.
            password (str): MongoDB password for authentication.
            db_name (str): Name of the database to connect to.
        """
        self.url = f"mongodb://{user}:{password}@{host}:27017/"
        self.db_name = db_name
        self.client = None
        self.db = None

        # Connecting to MongoDB
        self.connect()

        # Registering the disconnect method for execution upon program termination
        atexit.register(self.disconnect)

    def connect(self: Self) -> None:
        """Establish a connection to MongoDB.

        Attempts to connect to the MongoDB server and logs the result.
        Raises an exception if the connection fails.
        """
        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")  # Checking the connection
            logger.debug("Successfully connected to MongoDB!")
            self.db = self.client[self.db_name]
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def disconnect(self: Self) -> None:
        """Close the connection to MongoDB.

        Ensures that the MongoDB client is properly closed upon program termination.
        """
        if self.client:
            self.client.close()
            logger.debug("MongoDB connection closed.")

    def get_collection(self: Self, collection_name: str) -> Collection | None:
        """Get a collection by name from the current database.

        Args:
            collection_name (str): The name of the collection to retrieve.

        Returns:
            Collection: The MongoDB collection object.
        """
        return self.db[collection_name] if self.db is not None else None


class ReportRepository:
    COLLECTION_NAME: str = "compare_info"

    def __init__(self: Self, mongo_connection: MongoDBConnection) -> None:
        """Initialization of the repository for the compare_info collection."""
        collection = mongo_connection.get_collection(self.COLLECTION_NAME)
        if collection is None:
            logger.error('Mongo collection "%s" not found', self.COLLECTION_NAME)
            raise Exception('Mongo collection "%s" not found', self.COLLECTION_NAME)
        self.collection: Collection = collection

    def write_compare_info(
        self: Self, work1: ASTFeatures, work2: ASTFeatures, compare_info: CompareInfo
    ) -> None:
        """Insert or update a document in the compare_info collection.

        The primary key (_id) is formed as a dictionary with sorted file paths.

        Args:
            work1 (ASTFeatures): The first file for comparison.
            work2 (ASTFeatures): The second file for comparison.
            compare_info (CompareInfo): Information about the comparison results.
        """
        # Sorting paths to create a unique primary key
        work1, work2 = sorted([work1, work2])
        first_path, second_path = [str(work1.filepath), str(work2.filepath)]

        # Forming _id as a string of sorted paths
        document_id = {"first": first_path, "second": second_path}

        # Using the serialize_compare_result_to_dict function to convert data
        serialized_compare_info = serialize_compare_result_to_dict(compare_info)

        document = {
            "_id": document_id,
            "first_sha256": work1.sha256,
            "second_sha256": work2.sha256,
            "first_modify_date": work1.modify_date,
            "second_modify_date": work2.modify_date,
            "compare_info": serialized_compare_info,
        }

        # Insert or update the document
        self.collection.update_one({"_id": document_id}, {"$set": document}, upsert=True)
        logger.debug(f"Document for ({first_path}, {second_path}) successfully inserted/updated.")


class FeaturesRepository:
    COLLECTION_NAME: str = "features"

    def __init__(self: Self, mongo_connection: MongoDBConnection) -> None:
        """Initialization of the repository for the features collection."""
        collection = mongo_connection.get_collection(self.COLLECTION_NAME)
        if collection is None:
            logger.error('Mongo collection "%s" not found', self.COLLECTION_NAME)
            raise Exception('Mongo collection "%s" not found', self.COLLECTION_NAME)
        self.collection: Collection = collection

    def write_features(self: Self, work: ASTFeatures) -> None:
        """Insert or update a document in the features collection.

        The primary key (_id) is formed using the file path.

        Args:
            work (ASTFeatures): The file for which features are being saved.
        """
        # Forming _id as the file path
        document_id = str(work.filepath)

        # Using function serialize_features_to_dict to convert data
        serialized_work = serialize_features_to_dict(work)

        document = {
            "_id": document_id,
            "modify_date": work.modify_date,
            "sha256": work.sha256,
            "features": serialized_work,
        }

        # Insert or update the document
        self.collection.update_one({"_id": document_id}, {"$set": document}, upsert=True)
        logger.debug(f"Document for path {document_id} successfully inserted/updated.")


class MongoReporter(AbstractReporter):
    def __init__(self: Self, repository: ReportRepository) -> None:
        self.repository = repository

    def save_result(
        self: Self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
        compare_info: CompareInfo,
    ) -> None:
        """Updates the cache with new comparisons and writes it to the MongoDB.

        Args:
            first_work (ASTFeatures): Contains the first work metadata.
            second_work (ASTFeatures): Contains the second work metadata.
            compare_info (CompareInfo): Contains information about comparisons
              between the first and second works.
        """
        self.repository.write_compare_info(first_work, second_work, compare_info)

    def get_result(
        self: Self,
        first_work: ASTFeatures,
        second_work: ASTFeatures,
    ) -> CompareInfo | None:
        return None


class MongoFeaturesCache(AbstractFeaturesCache):
    def __init__(self: Self, repository: FeaturesRepository) -> None:
        self.repository = repository

    def save_features(self: Self, features: ASTFeatures) -> None:
        """Updates the cache with new work metadata and writes it to the MongoDB.

        Args:
            features (ASTFeatures): Contains work metadata.
        """
        self.repository.write_features(features)

    def get_features(self: Self, work: ASTFeatures) -> ASTFeatures | None:
        return None
