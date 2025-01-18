from fastapi import FastAPI
from router.chat_router import router as chat_router

# Initialize the FastAPI app
app = FastAPI()

# Include the chat router
app.include_router(chat_router)
