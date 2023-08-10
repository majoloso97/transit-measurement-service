from fastapi import APIRouter, Depends
from api.dependencies.auth import api_key_auth
from core.checks import checks


router = APIRouter(prefix='/api/v1')


@router.get('/checks/', dependencies=[Depends(api_key_auth)])
async def get_checks():
    return {"message": checks}
