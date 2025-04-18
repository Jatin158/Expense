# Use an official Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy project files to container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port Flask will run on
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
