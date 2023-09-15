# Path: db-population/db_initialization.py
import json
import os
from pydantic import BaseModel, AnyUrl
from typing import Deque, List, Optional, Tuple
from pymongo import MongoClient
from git import Repo


# Each license has a JSON file with the following structure:
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


# Creation of files from licenses.json

def create_files():
    # Read the licenses.json file
    with open("licenses.json", "r") as f:
        licenses = json.load(f)

    for license in licenses['licenses']:
        # Create a License object
        license_object = License(**license)
        # Create a file with the licenseId as name
        with open(f"../licenses/{license_object.licenseId}.json", "w") as f:
            # Write the JSON representation of the License object
            json.dump(license_object.model_dump(mode="json"), f, indent=4)

# Population of synonyms in files from spreadsheet
def populate_files_from_spreadsheet():
    # Open file of licenses_predictions 
    with open("licenses_predictions.tsv", "r") as f:
        lines = f.readlines()
    # For each line, get original license and the correct match (8th column)
    for line in lines:
        line = line.strip()
        line = line.split("\t")
        if len(line)>1:

            original_license = line[0]
            correct_match = line[1].strip()
            if correct_match:
                # exclude "NO VERSION NUMBER" and "TWO LICENSES" and "SEVERAL LICENSES" and "MORE THAN ONE LICENSE" and "NO LICENSE" and "AMBIGUOS"
                if correct_match.upper() in ["NO VERSION NUMBER", "NO LICENSE NUMBER","TWO LICENSES", "SEVERAL LICENSES", "MORE THAN ONE LICENSE", "NO LICENSE", "AMBIGUOS"]:
                    continue
                else:
                    # Check if the correct match has a file
                    if os.path.isfile(f"../licenses/{correct_match}.json"):
                        # Add the original license to the synonyms of the correct match
                        with open(f"../licenses/{correct_match}.json", "r") as f:
                            license = json.load(f)
                        if original_license not in license['synonyms']:
                            license['synonyms'].append(original_license)
                            with open(f"../licenses/{correct_match}.json", "w") as f:
                                json.dump(license, f, indent=4)
                    else:
                        print(f"File {correct_match}.json does not exist")
                        print(line)
                    pass
        else:
            continue

    return
    
# INITIAL POPULATION Population of database from files
def populate_db_from_files():
    '''
    This function populates the database with the licenses in the JSON files
    It uses "insert" instead of "update" so it can be used to populate an empty database
    Used for the initial population of the database
    '''
    # Connect to the database
    client = MongoClient('localhost', 27017)
    db = client['licenses']
    collection = db['licenses']
    # Open each file and populate the database
    for file in os.listdir("../licenses/"):
        with open(f"../licenses/{file}", "r") as f:
            license = json.load(f)
        # Create a License object
        license_object = License(**license)
        # Insert the license in the database
        collection.insert_one(license_object.dict())

    return


def modified_files(path: str):
    '''
    This function returns a list of the files that have been modified in the last commit
    '''
    repo = Repo(path)
    # Get the last commit
    last_commit = repo.head.commit
    prev_commits = [c for c in repo.iter_commits(all=True, max_count=2)]
    pre_last_commit = prev_commits[1]
    # Get the files that have been modified in the last commit
    modified_files = [item.a_path for item in pre_last_commit.diff(None)]
    return modified_files


# UPDATE licenses in database from files
def update_db_from_files():
    '''
    This function updates the database with the licenses in the JSON files
    It uses "update" instead of "insert" so it can be used to update an existing database
    '''
    # Connect to the database
    client = MongoClient('localhost', 27017)
    db = client['licenses']
    collection = db['licenses']
    # Open each file and populate the database
    mod_files = modified_files("../licenses/")

    for file in os.listdir("../licenses/"):
        with open(f"../{file}", "r") as f:
            license = json.load(f)
        # Create a License object
        license_object = License(**license)
        # Update the license in the database
        collection.update_one({"licenseId": license_object.licenseId}, {"$set": license_object.dict()})

    return


    

if __name__ == "__main__":
    #create_files()
    #populate_files_from_spreadsheet()
    print(modified_files("../"))
