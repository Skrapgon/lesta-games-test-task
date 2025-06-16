from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import check_password, create_access_token, hash_password, get_current_user, oauth2_scheme
from auth.blacklist import add_blacklist_token
from infra.database import get_db
from infra.models import User
from schema.token import TokenResponse
from schema.user import ChangePassword, UserOut, UserSchema

router = APIRouter(
    prefix='/api/auth',
    tags=['auth']
)

@router.post('/register', response_model=UserOut)
async def register(
    user_form: UserSchema,
    db: AsyncSession = Depends(get_db)
    ):
    
    result = await db.execute(select(User).where(User.username == user_form.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail='User already exists')

    user = User(
        username=user_form.username,
        password=hash_password(user_form.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut(username=user_form.username)
    
@router.post('/login', response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    ):
    
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalar_one_or_none()
    if not user or not check_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail='Incorrect login or password')

    access_token = create_access_token(subject=user.username)
    return TokenResponse(access_token=access_token, token_type='bearer')
    
@router.get('/logout')
async def logout(
    token: str = Depends(oauth2_scheme),
    user: User = Depends(get_current_user)
    ):
    
    result = await add_blacklist_token(token)
    if result:
        return {'status': 'logged out'}
    else:
        raise HTTPException(status_code=400, detail='Logout failed')

@router.patch('/change-password')
async def change_password(
    password_body: ChangePassword,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
    ):
    
    if not check_password(password_body.old_password, user.password):
        raise HTTPException(status_code=403, detail='Wrong old password')

    user.password = hash_password(password_body.new_password)
    db.add(user)
    await db.commit()
    return {'status': 'Password changed successfully'}

@router.delete('/', status_code=204)
async def delete_user(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    result = await add_blacklist_token(token)
    if result:
        await db.delete(current_user)
        await db.commit()
        return
    else:
        raise HTTPException(status_code=400, detail='Deletion failed')