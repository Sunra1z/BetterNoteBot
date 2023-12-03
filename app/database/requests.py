from app.database.models import User, Note, async_session
from sqlalchemy import select

async def get_notes(tg_id):
    async with async_session() as session:
        stmt = select(Note).where(Note.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().all()