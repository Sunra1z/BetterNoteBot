from database.models import User, Note, async_session
from sqlalchemy import select, delete


async def get_notes(tg_id):
    async with async_session() as session:
        stmt = select(Note).where(Note.tg_id == tg_id)
        result = await session.execute(stmt)
        return result.scalars().all()

async def delete_notes(tg_id, note_id):
    async with async_session() as session:
        stmt = delete(Note).where(Note.tg_id == tg_id).where(Note.id == note_id)
        await session.execute(stmt)
        await session.commit()
