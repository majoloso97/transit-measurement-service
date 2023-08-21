from fastapi import APIRouter


router = APIRouter(prefix='/api/v1')


@router.get('/welcome/')
async def welcome():
    return {"message": "Welcome to Transit Measurement API Service"}
