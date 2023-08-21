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

    def create_item(self, item_create: BaseModel) -> BaseModel:
        db_item = self.db_model(**item_create.dict())
        with self.db.get_session() as session:
            session.add(db_item)
            # session.refresh(db_item)
        return self.pydantic_response.from_orm(db_item)

    def get_item(self, item_id: int) -> BaseModel:
        with self.db.get_session() as session:
            db_item = session \
                        .query(self.db_model) \
                        .filter(self.db_model.id == item_id) \
                        .first()
        print(db_item)
        if db_item:
            return self.pydantic_response.from_orm(db_item)
        
    def get_item_by_field(self, **kwargs) -> BaseModel:
        with self.db.get_session() as session:
            db_item = session \
                        .query(self.db_model) \
                        .filter_by(**kwargs) \
                        .first()
        if db_item:
            return self.pydantic_response.from_orm(db_item)

    def update_item(self, item_id: int, item_update: BaseModel) -> BaseModel:
        with self.db.get_session() as session:
            db_item = session \
                        .query(self.db_model) \
                        .filter(self.db_model.id == item_id) \
                        .first()
            if db_item:
                for key, value in item_update.dict().items():
                    if value:
                        setattr(db_item, key, value)
                # session.refresh(db_item)
                return self.pydantic_response.from_orm(db_item)

    def delete_item(self, item_id: int):
        with self.db.get_session() as session:
            db_item = session \
                        .query(self.db_model) \
                        .filter(self.db_model.id == item_id) \
                        .first()
            if db_item:
                session.delete(db_item)

    def get_items(self):
        with self.db.get_session() as session:
            db_items = session.query(self.db_model).all()
        if db_items:
            func = self.pydantic_response.from_orm
            return [func(item) for item in db_items]
