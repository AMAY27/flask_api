# Use an official lightweight Python image.
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
       ffmpeg \
       portaudio19-dev \
       python3-dev \
       build-essential && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory.
WORKDIR /app

# Copy your requirements.txt first for caching.
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
       -i https://pypi.tuna.tsinghua.edu.cn/simple \
       --default-timeout=600 \
       -r requirements.txt
# Copy the rest of your app
COPY . .

# Expose the port your app runs on.
EXPOSE 5001

# Run the application using eventlet
CMD ["gunicorn", "-k", "eventlet", "-w", "1", "main:app", "--bind", "0.0.0.0:5001"]

