# Use python:3.11-slim-buster as a base image
FROM python:3.11-slim-buster
LABEL authors="spreis"

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies required for PyODBC, Node.js, and PostgreSQL
RUN apt-get update \
  && apt-get install -y build-essential curl unixodbc-dev gnupg g++ dos2unix \
  && curl -sL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get update \
  && apt-get install -y nodejs --no-install-recommends \
  && apt-get install -y libpq-dev \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean

# Create a non-root user 'python' and set ownership
RUN useradd --create-home python \
  && chown python:python -R /app

# Grant write permissions to all users for the /app directory and the home directory of the python user
# This is necessary for OpenShift which runs containers with arbitrary user IDs
RUN chmod -R 777 /app \
  && chmod -R 777 /home/python

# Switch to non-root user
USER python

# Copy Python requirements files and install Python dependencies
COPY --chown=python:python requirements*.txt ./
RUN pip install --upgrade pip \
  && pip install -r requirements.txt \
    && pip install waitress

# Set environment variables
ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python" \
    PYTHONPATH="/home/python/.local/lib/python3.11/site-packages"

# Copy the application source code
COPY --chown=python:python . .

# Copy the entrypoint script and make it executable
COPY entrypoint.sh /app/
RUN dos2unix /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Install Tailwind and build static files
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input
RUN SECRET_KEY=nothing python manage.py collectstatic --no-input

# Command to run the Django application
CMD ["./entrypoint.sh"]