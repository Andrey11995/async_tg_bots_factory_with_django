from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from bots.settings import with_session

metadata = MetaData()
Base = declarative_base()


class BaseTable(Base):
    __abstract__ = True
    __metadata__ = metadata

    @classmethod
    @with_session
    async def delete(cls, session: AsyncSession, obj):
        async with session.begin():
            await session.delete(obj)

    @classmethod
    @with_session
    async def get(cls, session: AsyncSession, **kwargs):
        return (await cls.filter(session=session, **kwargs)).one_or_none()

    @classmethod
    @with_session
    async def filter(cls, session: AsyncSession, order_by=None, limit=None, **kwargs):
        query = f'SELECT * FROM {cls.__tablename__}'
        conditions = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = '{value}'")
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        if order_by:
            if order_by.startswith('-'):
                order_by = f'{order_by[1:]} DESC'
            query += f' ORDER BY {order_by}'
        if limit:
            query += f' LIMIT {limit}'
        return (await session.execute(text(query))).unique()

    @classmethod
    @with_session
    async def create(cls, session: AsyncSession, **kwargs):
        instance = cls(**kwargs)
        async with session.begin():
            session.add(instance)
        return instance

    @classmethod
    @with_session
    async def get_or_create(cls, session: AsyncSession, defaults=None, **kwargs):
        async with session.begin():
            instance = await cls.get(session=session, **kwargs)
            if instance:
                instance = cls(**instance._asdict())
                created = False
            else:
                defaults = defaults if defaults else {}
                instance = cls(**kwargs, **defaults)
                session.add(instance)
                created = True
        return instance, created

    @with_session
    async def update(self, session: AsyncSession, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        async with session.begin():
            await session.merge(self)

    @classmethod
    @with_session
    async def count(cls, session: AsyncSession, **kwargs):
        query = f'SELECT COUNT(*) FROM {cls.__tablename__}'
        conditions = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = '{value}'")
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        return (await session.execute(text(query))).scalar()

    @classmethod
    @with_session
    async def exists(cls, session: AsyncSession, **kwargs):
        query = f'SELECT EXISTS(SELECT 1 FROM {cls.__tablename__}'
        conditions = []
        for key, value in kwargs.items():
            conditions.append(f"{key} = '{value}'")
        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)
        query += ')'
        return (await session.execute(text(query))).scalar()
