# Pull official base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y gcc python3-dev musl-dev libmagic1

COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r ./requirements.txt

# Copy entrypoint.sh
COPY ./docker/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

COPY . /app

ENTRYPOINT [ "/entrypoint.sh" ]