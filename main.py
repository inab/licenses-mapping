from fastapi import FastAPI, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from utils import connect_db, License
from pydantic import BaseModel, Field
from typing import Union
from typing_extensions import Annotated
from dotenv import load_dotenv
from git import Repo
import json
import os
import urllib.parse

# Load environment variables
load_dotenv()

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
    },
    root_path="/licenses-mapping"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/licenses/{license_id}")
def read_license(
    license_id: str = Path(
        title="License ID",
        description="The SPDX ID of the license",
        examples="AGPL-3.0-only",
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
        examples="AGPL-3.0-only",
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
        examples="GNU General Public License, version 2",
        )
    ):
    '''
    This function maps the license to the SPDX license list
    '''
    # Connect to the database
    collection = connect_db()
    # Get the license
    decoded_q = urllib.parse.unquote(q)
    license = collection.find_one({ "$or": [ { "licenseId": decoded_q }, { "synonyms": decoded_q } ] }, {"_id": 0, "reference": 1, "licenseId":1, "name":1, "isOsiApproved": 1, "isDeprecatedLcenseId":1, "seeAlso":1 } )

    return license


# UPDATE licenses in database from files
def update_db_from_files():
    '''
    This function updates the database with the licenses in the JSON files
    It uses "update" instead of "insert" so it can be used to update an existing database
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
        modified = collection.update_one({"licenseId": license_object.licenseId}, {"$set": license_object.model_dump(mode="json")})
        N+=modified.modified_count

    return N

class Payload(BaseModel):
    state: str = Field(examples=["ping"])

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
        url = "git@github.com:inab/licenses-mapping.git"
        repo = Repo("./")
        origin = repo.remotes.origin
        origin.set_url(url)
        origin.pull('main')

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
    
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=3200, log_level='debug')
