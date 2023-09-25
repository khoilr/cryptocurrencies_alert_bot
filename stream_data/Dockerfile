# Use the official Python Alpine image as a parent image
FROM python:3.11

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install any needed packages specified in requirements.stream_data.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY main.py .
COPY bitget bitget

# Run your Python script when the container launches
CMD ["python", "main.py"]
