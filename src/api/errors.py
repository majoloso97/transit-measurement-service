from fastapi import HTTPException


def raise_http_exception(code: int, detail: str, headers: dict = None):
    raise HTTPException(status_code=code,
                        detail=detail,
                        headers=headers)
