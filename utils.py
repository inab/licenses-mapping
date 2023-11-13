from pydantic import BaseModel, AnyUrl
from typing import List
from pymongo import MongoClient
import os


def connect_db():
    '''
    This function connects to the database and returns the collection
    '''
    # Connect to the database
        # variables come from .env file
    mongoHost = os.getenv('MONGO_HOST', default='localhost')
    mongoPort = os.getenv('MONGO_PORT', default='27017')
    mongoUser = os.getenv('MONGO_USER')
    mongoPass = os.getenv('MONGO_PWD')
    mongoAuthSrc = os.getenv('MONGO_AUTH_SRC')
    mongoDb = os.getenv('MONGO_DB')
    mongoCollection = os.getenv('MONGO_COLLECTION',)

    # Connect to MongoDB
    mongoClient = MongoClient(
        host=mongoHost,
        port=int(mongoPort),
        username=mongoUser,
        password=mongoPass,
        authSource=mongoAuthSrc,
    )
    db = mongoClient[mongoDb]
    collection = db[mongoCollection]

    print(f"Connected to MongoDB at {mongoHost}:{mongoPort} as {mongoUser} on database {mongoDb} and collection {mongoCollection}")
    return collection

class License(BaseModel):
    # from SPDX model https://spdx.org/licenses/:
    reference: AnyUrl
    licenseId: str
    name: str
    isOsiApproved: bool
    isDeprecatedLicenseId: bool
    seeAlso: List[AnyUrl]
    # custom fields:
    synonyms: List[str] = []
