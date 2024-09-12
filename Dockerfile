#!/bin/bash
FROM python:3.8

# ------  Configuring ssh to allow connecting to GitHub ------
# Install necessary dependencies
RUN apt-get update && apt-get install -y git openssh-client

# Create the .ssh directory
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# Add the SSH config to force GitHub to use the custom port
RUN echo "Host github.com\n\
  Hostname ssh.github.com\n\
  Port 443" > /root/.ssh/config && \
    chmod 600 /root/.ssh/config

# Add GitHub's SSH key to known_hosts to prevent the trust prompt
RUN ssh-keyscan -p 443 ssh.github.com >> /root/.ssh/known_hosts

# ------ The API ------

COPY . .

RUN python3 -m pip install -r requirements.txt --no-dependencies

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000
