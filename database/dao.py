from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User


class DatabaseWork:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_user_in_db(self, data: dict):
        self.session.add(User(**data))
        await self.session.commit()
        return {"success": "user add in database"}

    async def get_user_from_db(self, username: str):
        result = await self.session.execute(select(User).where(User.username==username))
        user = result.scalar_one_or_none()
        if user:
            return user
        return {"except": f"not found {username}"}