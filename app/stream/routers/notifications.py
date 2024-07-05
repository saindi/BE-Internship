import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from auth.auth import jwt_bearer
from db.database import get_async_session
from user.models.models import UserModel, NotificationModel
from user.schemas import NotificationSchema
from stream.connection_manager import manager

router = APIRouter()


@router.websocket("/user_notifications/{user_id}/")
async def websocket_endpoint(
        user_id: int,
        token: str,
        websocket: WebSocket,
        db: AsyncSession = Depends(get_async_session)
):
    user = await jwt_bearer.verify(token=token)

    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token error")

    if not user.can_read(user_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No permission")

    await manager.connect(websocket)

    latest_notification_time = None

    try:
        while True:
            filters = {'id_user': user_id}
            if latest_notification_time:
                filters['created_at'] = {'gt': latest_notification_time}

            notifications = await NotificationModel.get_by_fields(db, return_single=False, **filters)

            if notifications:
                notification_schemas = [NotificationSchema.model_validate(notification) for notification in notifications]
                await websocket.send_json([notification.dict() for notification in notification_schemas])

                latest_notification_time = max(notification.created_at for notification in notifications)

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
