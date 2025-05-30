
# Python Audio Processing Application

This is a Python-based application designed for real-time audio stream analysis and event detection. The application is containerized using Docker and deployed with Gunicorn using the `eventlet` worker.

## 🚀 Features

- Real-time audio processing using `ffmpeg` and `portaudio`
- Event-driven architecture with Flask
- Containerized using Docker for easy deployment
- Exposes a REST API on port `5001`

## 🛠️ Requirements

- Docker (recommended)
- (Optional) Python 3.10+ if running locally

## 🧱 Getting Started

### 🔧 Build the Docker Image

Build the Docker image from the root of your project directory:

```bash
docker build -t audio-analysis-app .
````

### ▶️ Run the Docker Container

Start the container and map port 5001:

```bash
docker run -p 5001:5001 audio-analysis-app
```

Visit the frontend application and test the live streaming and check the logs in the Docker desktop.

## 📁 Project Structure

```
/app
│
├── main.py              # Entry point for Flask app
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container specification
└── ...                  # Other source files and modules
```

## 🐳 Dockerfile Breakdown

```dockerfile
# Use an official lightweight Python image.
FROM python:3.10-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
       ffmpeg \
       portaudio19-dev \
       python3-dev \
       build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
       -i https://pypi.tuna.tsinghua.edu.cn/simple \
       --default-timeout=600 \
       -r requirements.txt

COPY . .

EXPOSE 5001

CMD ["gunicorn", "-k", "eventlet", "-w", "1", "main:app", "--bind", "0.0.0.0:5001"]
```

## 👤 Author

**Amay Rajvaidya**
📫 [rajvaidyaamay27@gmail.com](mailto:rajvaidyaamay27@gmail.com)
🔗 [GitHub Profile](https://github.com/AMAY27)


