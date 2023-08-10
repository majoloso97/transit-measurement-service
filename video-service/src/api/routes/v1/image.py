from fastapi import APIRouter, Depends
from api.dependencies.auth import api_key_auth
from core.model import main


router = APIRouter(prefix='/api/v1')


@router.get('/image/', dependencies=[Depends(api_key_auth)])
async def get_checks():
    main()
    return {"message": 'Runs'}
