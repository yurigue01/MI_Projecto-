# Use the official Node.js image as a base image
FROM node:14-alpine

# Set the working directory inside the container
WORKDIR /app

# Copy the package.json and package-lock.json files from the "frontend" directory to the current directory in the container
COPY frontend/package.json frontend/package-lock.json ./

# Install dependencies
RUN npm install

# Copy the remaining frontend files from the "frontend" directory to the current directory in the container
COPY frontend/ .

# Build the frontend
RUN npm run build

# Expose the port on which your frontend application will run
EXPOSE 3000

# Command to run your frontend application
CMD ["npm", "start"]
