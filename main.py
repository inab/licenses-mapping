from fastapi import FastAPI, Query, Path
from utils import connect_db, License
from pydantic import BaseModel, AnyUrl
from typing import Union
from typing_extensions import Annotated
from git import Repo
import json
import os


app = FastAPI(
    title="License Mapping API",
    description="This API allows to map license strings to a SPDX licenses and get licenses information",
    version="0.1.0",
    contact={
        "name": "Eva Martin",
        "email": "eva.martin@bsc.es",
        },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    }
)

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


# UPDATE licenses in database from files
def update_db_from_files():
    '''
    This function updates the database with the licenses in the JSON files
    It uses "update" instead of "insert" so it can be used to update an existing database
    🚧 NOT TESTED YET
    '''
    # Connect to the database
    collection = connect_db()
    # iterate all files in licenses folder
    N=0
    for file in os.listdir("./licenses/"):
        with open(f"./licenses/{file}", "r") as f:
            license = json.load(f)
        # Create a License object
        license_object = License(**license)
        # Update the license in the database
        collection.update_one({"licenseId": license_object.licenseId}, {"$set": license_object.model_dump(mode="json")})
        N+=1

    return N

class Payload(BaseModel):
    state: str

# Webhooks 
@app.post("/webhooks")
def webhooks(
    payload: Union[Annotated[Payload, "The payload of the webhook"], BaseModel]
    ):
    '''
    This function receives a webhook
    '''
    if payload.state == 'updated':
        # Pull changes from the remote repository
        repo = Repo("./")
        origin = repo.remotes.origin
        origin.pull()

        # Update the database
        N = update_db_from_files()

        return {
            "status": "success",
            "message": f"{N} documents updated in database"
            }
    
    if payload.state == 'ping':
        return {
            "status": "success",
            "message": "pong from License Mapping API 👋🏻"
            }
    else:
        return payload
    
