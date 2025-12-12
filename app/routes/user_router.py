from fastapi import APIRouter, Depends, HTTPException
from app.services.user_service import UserService

user_router = APIRouter(prefix="/users")
