#!/bin/bash
FROM python:3.8
COPY . .

RUN python3 -m pip install -r requirements.txt --no-dependencies

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
