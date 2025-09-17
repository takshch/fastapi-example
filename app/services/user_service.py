from typing import Optional
from app.database import get_database
from app.schemas.user import UserCreate, UserLogin
from app.auth import verify_password, get_password_hash, create_access_token
from fastapi import HTTPException, status
from datetime import timedelta

class UserService:
    def __init__(self):
        self.collection_name = "users"

    async def get_collection(self):
        """Get the users collection"""
        database = await get_database()
        return database[self.collection_name]

    async def create_user(self, user: UserCreate) -> dict:
        """Create a new user"""
        collection = await self.get_collection()
        
        # Check if user already exists
        existing_user = await collection.find_one({"username": user.username})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create user document
        user_dict = {
            "username": user.username,
            "hashed_password": hashed_password
        }
        
        result = await collection.insert_one(user_dict)
        
        return {"username": user.username, "id": str(result.inserted_id)}

    async def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user"""
        collection = await self.get_collection()
        user = await collection.find_one({"username": username})
        
        if not user:
            return None
        
        if not verify_password(password, user["hashed_password"]):
            return None
        
        return {"username": user["username"]}

    async def login_for_access_token(self, user_login: UserLogin) -> dict:
        """Login user and return access token"""
        user = await self.authenticate_user(user_login.username, user_login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}

# Create a global instance
user_service = UserService()
