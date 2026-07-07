import os

def get_headers() -> dict: 
    """Return Alpaca API headers from .env file."""
    
    api_key = os.getenv("APCA_API_KEY_ID")
    secret_key = os.getenv("APCA_API_SECRET_KEY")
    
    if not api_key or not secret_key:
        raise ValueError(
            "API keys not found! Check your .env file and make sure load_dotenv() is called."
        )
    
    return {
        "accept": "application/json",
        "APCA-API-KEY-ID": api_key,
        "APCA-API-SECRET-KEY": secret_key,
    }
