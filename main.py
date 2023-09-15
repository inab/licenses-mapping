from fastapi import FastAPI, Query, Path
from utils import connect_db, License
from pydantic import BaseModel, AnyUrl
from typing import Union
from typing_extensions import Annotated

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/licenses/{license_id}")
def read_license(
    license_id: str = Path(
        title="License ID",
        description="The SPDX ID of the license",
        example="AGPL-3.0-only",
        )
    ):
    '''
    This function returns the license with the given license_id
    '''
    # Connect to the database
    collection = connect_db()
    # Get the license
    license = collection.find_one({"licenseId": license_id}, {"_id": 0, "reference": 1, "licenseId":1, "name":1, "isOsiApproved": 1, "isDeprecatedLcenseId":1, "seeAlso":1 })
    return license

@app.get("/licenses/{license_id}/synonyms")
def read_license_synonyms(
    license_id: str = Path(
        title="License ID",
        description="The SPDX ID of the license",
        example="AGPL-3.0-only",
        )
    ):
    # Connect to the database
    collection = connect_db()
    license = collection.find_one({"licenseId": license_id}, {"_id": 0, "licenseId":1, "synonyms": 1 })
    return license


@app.post("/map")
def map_license_string(
    q: str = Query(
        title="License string",
        description="The license string to be mapped.",
        example="GNU General Public License, version 2",
        )
    ):
    '''
    This function maps the license to the SPDX license list
    '''
    # Connect to the database
    collection = connect_db()
    # Get the license
    license = collection.find_one({ "$or": [ { "licenseId": q }, { "synonyms": q } ] }, {"_id": 0, "reference": 1, "licenseId":1, "name":1, "isOsiApproved": 1, "isDeprecatedLcenseId":1, "seeAlso":1 } )

    return license