# Use the official Python image as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file from your host to the current directory in the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code to the container
COPY . .

# Expose the port on which your backend application will run
EXPOSE 8000

# Command to run your backend application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



