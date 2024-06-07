import shutil

from fastapi import File, UploadFile, Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from pathlib import Path


from auth.auth import jwt_bearer
from db.database import get_async_session
from user.models.models import UserModel

router = APIRouter()

AVATAR_DIR = Path("media/avatars")
AVATAR_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload_avatar/{user_id}/")
async def upload_avatar(
        user_id: int,
        file: UploadFile = File(...),
        user: UserModel = Depends(jwt_bearer),
        db: AsyncSession = Depends(get_async_session)
):
    affected_user = await UserModel.get_by_id(db, user_id)

    if not user.can_edit(affected_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This user cannot change the data')

    file_path = AVATAR_DIR / f"{user_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await affected_user.update(db, {"avatar": str(file_path)})

    return affected_user
