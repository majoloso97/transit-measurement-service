from fastapi import APIRouter, Depends
from api.dependencies.auth import api_key_auth


router = APIRouter(prefix='/api/v1')


@router.get('/welcome/')
async def welcome():
    return {"message": "Welcome to Transit Measurement Video Processing Service"}


@router.get('/protected/', dependencies=[Depends(api_key_auth)])
async def protected():
    return {"message": 'Accessing protected view'}