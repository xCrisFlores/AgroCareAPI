import time
from dotenv import load_dotenv
import jwt
import os 

load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"

def create_jwt(payload: dict, expire_in_sec=None):
    if expire_in_sec:
        payload["exp"] = int(time.time()) + expire_in_sec
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt(token: str):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        print(f"Token verificado exitosamente: {decoded}")
        return decoded
        
    except jwt.ExpiredSignatureError as e:
        print(f"Token expirado: {e}")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Token inválido: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None