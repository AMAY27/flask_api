import websockets
import asyncio
from locust import User, task, between
import gevent
from gevent import monkey
import time
import json

# Monkey-patch all necessary modules for gevent to work with asyncio
monkey.patch_all()

class WebSocketAudioUser(User):
    wait_time = between(1, 5)  # Time between tasks (simulate real users)

    def on_start(self):
        """Called when a simulated user starts."""
        # WebSocket connection setup
        # Start the asyncio loop explicitly within gevent context
        gevent.spawn(self.connect_ws)
    
    def connect_ws(self):
        """This method handles WebSocket connection."""
        asyncio.run(self.ws_connect())
        
    async def ws_connect(self):
        """Establish WebSocket connection using asyncio"""
        self.ws = await websockets.connect('ws://localhost:5001')  # Your WebSocket server address
        print("WebSocket connected")

    @task
    async def send_audio_chunk(self):
        """Simulate sending audio chunk to the backend."""
        # Simulate sending audio data (you can replace this with real audio data in the future)
        audio_data = b'\x00' * 1024  # Placeholder for raw audio chunk data
        timestamp = int(time.time() * 1000)  # Get current timestamp in milliseconds
        
        # Create the message to send to the backend (audio data and timestamp)
        message = json.dumps({
            "audio_data": audio_data.hex(),  # Convert audio data to hex to send over WebSocket
            "timestamp": timestamp
        })
        
        # Send the audio data over WebSocket
        await self.ws.send(message)

    def on_stop(self):
        """Called when a simulated user stops."""
        # Close the WebSocket connection when the user stops
        self.ws.close()
        print("WebSocket connection closed")
