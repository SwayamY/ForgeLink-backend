# Use official Python image
FROM python:3.12

# Set the working directory
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Add and make the start script executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Expose port (FastAPI runs on 8000 by default)
EXPOSE 8000


CMD ["/start.sh"]
