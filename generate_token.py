"""Generate test JWT token for aegisai-connectors API testing."""

from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def generate_test_token(user_id: str = None) -> str:
    """Generate a test JWT token."""
    if user_id is None:
        user_id = str(uuid.uuid4())
    
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token, user_id


if __name__ == "__main__":
    token, user_id = generate_test_token()
    print("\n" + "="*80)
    print("TEST JWT TOKEN FOR AEGISAI-CONNECTORS")
    print("="*80)
    print(f"\nUser ID: {user_id}")
    print(f"\nToken:\n{token}\n")
    print("="*80)
    print("\nUse in Postman:")
    print(f'Authorization: Bearer {token}')
    print("="*80 + "\n")
