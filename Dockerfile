# Use an official Python runtime as a parent image
FROM python:3.7 AS builder

# Set the working directory in the container
WORKDIR /app/python

# Copy the requirements file and install dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Download additional resources
RUN python -m spacy download en

# Copy the rest of the application code
COPY . /app

# Expose port 5000 to the outside world
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=ChatBot.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the application
# Set the default command to run the application
CMD ["python3", "ChatBot.py"]
