# Use python:3.11-slim-buster as a base image
FROM python:3.11-slim-buster
LABEL authors="spreis"

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies required for PyODBC and Node.js
RUN apt-get update \
  && apt-get install -y build-essential curl unixodbc-dev gnupg \
  && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean

# Add Microsoft repository key and repository for SQL Server ODBC Driver
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
  && curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install Microsoft ODBC Driver for SQL Server
RUN apt-get update \
  && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Create a non-root user 'python' and set ownership
RUN useradd --create-home python \
  && chown python:python -R /app

# Switch to non-root user
USER python

# Copy Python requirements files and install Python dependencies
COPY --chown=python:python requirements*.txt ./
RUN pip install --upgrade pip \
  && pip install -r requirements.txt

# Set environment variables
ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

# Copy the application source code
COPY --chown=python:python . .

# Install Tailwind and build static files
RUN SECRET_KEY=nothing python manage.py tailwind install --no-input
RUN SECRET_KEY=nothing python manage.py tailwind build --no-input
RUN SECRET_KEY=nothing python manage.py collectstatic --no-input

# Command to run the Django application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
