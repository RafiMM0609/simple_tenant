from typing import List, Any, Type, Optional
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from pytz import timezone
from models import supabase, get_supabase
from jose import JWTError, jwt
from settings import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, TZ

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def generate_hash_password(password: str) -> str:
    print("Input password:", password)
    
    salt = bcrypt.gensalt()
    print("Generated salt:", salt)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    print("Hashed password:", hashed_password)
    
    return hashed_password.decode('utf-8')

def generate_hash_lisensi(lisensi: str) -> str:
    hash = bcrypt.hashpw(str.encode(lisensi), bcrypt.gensalt())
    return hash.decode()


def validated_user_password(hash: str, password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hash.encode())
    except:
        return False


async def generate_jwt_token_from_user(
    user: Type[Any], ignore_timezone: bool = False
) -> str:
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if ignore_timezone == False:
        expire = expire.astimezone(timezone(TZ))
    payload = {
        "user_id": str(user['user_id']),
        "username": user['username'],
        "email": user['email'],
        "exp": expire,
    }
    jwt_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_token


def get_user_from_jwt_token(db: any, model: str, jwt_token: str) -> Optional[Type[Any]]:
    try:
        payload = jwt.decode(token=jwt_token, key=SECRET_KEY, algorithms=ALGORITHM)
        if payload["exp"] < datetime.now().timestamp():
            return None
        id = payload.get("id")
        response = supabase.table(model).select("*").eq("id", id).execute()
    except JWTError:
        return None
    except Exception as e:
        print(e)
        return None
    return response.data[0]


