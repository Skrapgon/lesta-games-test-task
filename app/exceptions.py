from fastapi import HTTPException, status

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

document_404 = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Document not found')

collection_404 = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Collection not found')

access_denied_403 = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access denied')