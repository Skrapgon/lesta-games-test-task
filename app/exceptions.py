from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

document_404 = HTTPException(status_code=404, detail='Document not found')

collection_404 = HTTPException(status_code=404, detail='Collection not found')

access_denied_403 = HTTPException(status_code=403, detail='Access denied')