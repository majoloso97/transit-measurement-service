from fastapi import APIRouter, Depends
from api.dependencies.auth import api_key_auth
from database.models import printing


router = APIRouter(prefix='/api/v1')


@router.get('/welcome/')
async def welcome():
    return {"message": "Welcome to Transit Measurement API Service"}


@router.get('/protected/', dependencies=[Depends(api_key_auth)])
async def protected():
    return {"message": f'Yes, {printing()}'}
