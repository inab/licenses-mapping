from pydantic import BaseModel, AnyUrl
from typing import List
from pymongo import MongoClient


def connect_db():
    '''
    This function connects to the database and returns the collection
    '''
    # Connect to the database
    client = MongoClient('localhost', 27017)
    db = client['licenses']
    collection = db['licenses']
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
