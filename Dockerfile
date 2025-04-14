# Use official Python base image
FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Copy dependency file and install packages
COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc libffi-dev libssl-dev \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
###########