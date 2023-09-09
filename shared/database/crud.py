from pydantic import BaseModel
from sqlalchemy.ext.declarative import DeclarativeMeta
from shared.database.db import db


class CRUDManager:
    def __init__(self,
                 db_model: DeclarativeMeta,
                 pydantic_create: BaseModel,
                 pydantic_update: BaseModel,
                 pydantic_response: BaseModel):
        self.db = db
        self.db_model = db_model
        self.pydantic_create = pydantic_create
        self.pydantic_update = pydantic_update
        self.pydantic_response = pydantic_response

    def create_item(self, session, item_create: BaseModel) -> BaseModel:
        if not isinstance(item_create, self.pydantic_create):
            err = 'Parameter item_create does not match the expected model'
            raise TypeError(err)

        db_item = self.db_model(**item_create.dict())
        session.add(db_item)
        session.commit()
        created = self.pydantic_response.from_orm(db_item)
        return created

    def get_item(self, session, item_id: int) -> BaseModel:
        db_item = session \
                    .query(self.db_model) \
                    .filter(self.db_model.id == item_id) \
                    .first()
        if db_item:
            return self.pydantic_response.from_orm(db_item)
        
    def get_item_by_field(self, session, **kwargs) -> BaseModel:
        db_item = session \
                    .query(self.db_model) \
                    .filter_by(**kwargs) \
                    .first()
        if db_item:
            return self.pydantic_response.from_orm(db_item)

    def update_item(self, session, item_id: int, item_update: BaseModel) -> BaseModel:
        if not isinstance(item_update, self.pydantic_update):
            err = 'Parameter item_update does not match the expected model'
            raise TypeError(err)

        db_item = session \
                    .query(self.db_model) \
                    .filter(self.db_model.id == item_id) \
                    .first()
        if db_item:
            for key, value in item_update.dict().items():
                if value:
                    setattr(db_item, key, value)
            # session.refresh(db_item)
            session.commit()
            return self.pydantic_response.from_orm(db_item)

    def delete_item(self, session, item_id: int):
        db_item = session \
                    .query(self.db_model) \
                    .filter(self.db_model.id == item_id) \
                    .first()
        if db_item:
            session.delete(db_item)
            session.commit()

    def get_items(self, session):
        db_items = session.query(self.db_model).all()
        if db_items:
            func = self.pydantic_response.from_orm
            return [func(item) for item in db_items]
