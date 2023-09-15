# License Mapping API 


[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 

## Overview
[API Documentation]()


## dev
Start the server with:
```python
python3 -m uvicorn main:app --reload
``` 

## Licenses Data
SPDX licenses metadata and synonyms are stored in the files of the `data` directory. The database is generated and updated from these files. The update is triggered by commmits being pushed to `main` branch. 

## Webhooks 
The API is configured to listen to the following webhooks:
- `update`: update the database
- `ping`: ping the server

