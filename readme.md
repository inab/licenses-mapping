# License Mapping API 

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) 


## Overview
A tool to map strings to SPDX licenses names or IDs. 

📄 [API Documentation](https://observatory.openebench.bsc.es/licenses-mapping/docs) 

🐳 [Docker image](https://hub.docker.com/repository/docker/emartps/license-mapping-api/general)

## Licenses Data
SPDX licenses metadata and synonyms are stored in the files of the `licenses` directory. The database is generated and updated from these files. The update is triggered by commmits being pushed to `main` branch. 

### 🙌🏻 Contribution to licenses synonyms 
To contribute to the licenses synonyms, please edit the files in the `licenses` directory and submit a pull request.

## Webhooks 
The API is configured to listen to the following webhooks:
- `update`: update the database
- `ping`: ping the server

## CI - Database Update 
The database is updated by the following GitLab CI workflow:

```yaml
stages:
  - webhook

update:
  stage: webhook
  variables:
    DEPLOY_CURL_COMMAND: 'curl -H "Content-Type: application/json" --data @data.json https://396e-84-88-188-229.ngrok-free.app/webhooks'
  script:
    - 'eval "$DEPLOY_CURL_COMMAND"'
  rules:
    - changes:
      - licenses/*
      when: on_success
```


## Development
Start the server with:
```python
python3 -m uvicorn main:app --reload
``` 