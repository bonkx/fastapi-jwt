import uuid
from typing import Any, Dict, Generic, List, Sequence, Type, TypeVar

from fastapi_pagination.ext.async_sqlmodel import paginate
from sqlalchemy.sql.expression import Executable

from ..services.base import SessionMixin


class BaseRepository(SessionMixin):
    """Base repository class responsible for operations over database."""

    async def get_all(self, statement: Executable) -> List[Any]:
        return await paginate(session=self.session, query=statement)

    async def get_one(self, statement: Executable) -> Any:
        result = await self.session.exec(statement)
        obj = result.first()

        return obj if obj is not None else None

    async def add_one(self, model: Any) -> None:
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return model.model_dump()

    # def add_all(self, models: Sequence[Any]) -> None:
    #     self.session.add_all(models)

    async def delete_one(self, model: Any) -> None:
        await self.session.delete(model)
        await self.session.commit()

        return model


# T = TypeVar("T", bound=SQLModel)


# class BaseRepository(Generic[T]):
#     def __init__(self, model: Type[T], session: Session):
#         self.model = model
#         self.session = session

#     def create(self, data: Dict[str, Any], commit=True) -> T:
#         try:
#             obj = self.model(**data)
#             self.session.add(obj)
#             if commit:
#                 self.session.commit()
#                 self.session.refresh(obj)
#             return obj
#         except Exception as e:
#             self.session.rollback()
#             raise HTTPException(status_code=400, detail=str(e))

#     def get(self, id: uuid.UUID) -> T:
#         return self.session.get(self.model, id)

#     def get_all(self) -> List[T]:
#         statement = select(self.model)
#         return self.session.exec(statement).all()

#     def update(self, id: uuid.UUID, data: Dict[str, Any], commit=True) -> T:
#         obj = self.session.get(self.model, id)
#         if not obj:
#             raise HTTPException(status_code=404, detail="Item not found")

#         for key, value in data.items():
#             setattr(obj, key, value)

#         if commit:
#             self.session.commit()
#             self.session.refresh(obj)

#         return obj

#     def delete(self, id: uuid.UUID, commit=True) -> bool:
#         obj = self.session.get(self.model, id)
#         if not obj:
#             raise HTTPException(status_code=404, detail="Item not found")

#         self.session.delete(obj)
#         if commit:
#             self.session.commit()
#         return True
