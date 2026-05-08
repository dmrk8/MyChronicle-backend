from typing import Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from pymongo import ReturnDocument
import structlog

from app.models.db.db_context_model import DBOpContext
from app.repositories._repo_observability import run_db_op

from pymongo.results import InsertOneResult, DeleteResult

from app.utils.time_helpers import utc_now

logger = structlog.getLogger()

DBModel = TypeVar("DBModel", bound=BaseModel)
InsertModel = TypeVar("InsertModel", bound=BaseModel)
UpdateModel = TypeVar("UpdateModel", bound=BaseModel)
UpsertModel = TypeVar("UpsertModel", bound=BaseModel)


class BaseRepository(Generic[DBModel]):
    db_model: Type[DBModel]

    def __init__(self, db, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
        self.logger = logger.bind(
            repository=self.__class__.__name__, collection=collection_name
        )

    def _make_context(self, operation: str, **kwargs) -> DBOpContext:
        return DBOpContext(
            operation=operation,
            collection=self.collection.name,
            **kwargs,
        )

    def _event(self, action: str) -> tuple[str, str]:
        """Returns (success_event, error_event) derived from the collection name

        Args:
            action (str): The action being performed, e.g. "insert_one", "update_one", etc.

        Returns:
            tuple[str, str]: A tuple containing the success event name and error event name
        """
        base = f"mongo_{self.collection.name}"
        return (
            f"{base}_{action}",
            f"{base}_{action}_error",
        )

    async def _find_one(self, query: dict, context: DBOpContext) -> DBModel | None:
        success_event, error_event = self._event("find_one")

        async def _op():
            return await self.collection.find_one(query)

        doc = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return self.db_model.model_validate(doc) if doc else None

    async def _find_many(
        self,
        query: dict,
        context: DBOpContext,
        sort_by: Optional[str] = None,
        sort_order: int = 1,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> List[DBModel]:
        success, error = self._event("find")

        async def _op():
            cursor = self.collection.find(query)
            if sort_by:
                cursor = cursor.sort(sort_by, sort_order)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            return [self.db_model.model_validate(doc) async for doc in cursor]

        return await run_db_op(
            self.logger, _op, success_event=success, error_event=error, context=context
        )

    async def _delete_one(self, query: dict, context: DBOpContext) -> bool:
        success_event, error_event = self._event("delete_one")

        async def _op() -> DeleteResult:
            return await self.collection.delete_one(query)

        result = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return result.deleted_count > 0

    async def _delete_many(self, query: dict, context: DBOpContext) -> bool:
        success_event, error_event = self._event("delete_many")

        async def _op() -> DeleteResult:
            return await self.collection.delete_many(query)

        result = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return result.deleted_count > 0

    async def _count(self, query: dict, context: DBOpContext) -> int:
        success_event, error_event = self._event("count")

        async def _op() -> int:
            return await self.collection.count_documents(query)

        return await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )


class CRUDRepository(
    BaseRepository[DBModel], Generic[DBModel, InsertModel, UpdateModel]
):
    async def _insert(self, data: InsertModel, context: DBOpContext) -> DBModel:
        raw = data.model_dump()
        raw["created_at"] = utc_now()
        raw["updated_at"] = utc_now()

        success_event, error_event = self._event("insert_one")

        async def _op() -> InsertOneResult:
            return await self.collection.insert_one(raw)

        result = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return self.db_model.model_validate({**raw, "_id": result.inserted_id})

    async def _find_one_and_update(
        self, query: dict, update: UpdateModel, context: DBOpContext
    ) -> Optional[DBModel]:
        data = update.model_dump(exclude_unset=True)
        data["updated_at"] = utc_now()

        success_event, error_event = self._event("find_one_and_update")

        async def _op():
            return await self.collection.find_one_and_update(
                query,
                {"$set": data},
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return self.db_model.model_validate(doc) if doc else None

    async def _update_one(
        self, query: dict, update: dict, context: DBOpContext
    ) -> bool:
        success_event, error_event = self._event("update_one")

        async def _op():
            return await self.collection.update_one(query, {"$set": update})

        result = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return result.modified_count > 0

    async def _update_many(
        self, query: dict, update: dict, context: DBOpContext
    ) -> bool:
        success_event, error_event = self._event("update_many")

        async def _op():
            return await self.collection.update_many(query, {"$set": update})

        result = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return result.modified_count > 0


class UpsertRepository(BaseRepository[DBModel], Generic[DBModel]):
    async def _upsert(
        self, filter_query: dict, update_doc: dict, context: DBOpContext
    ) -> DBModel:
        success_event, error_event = self._event("upsert")

        async def _op():
            return await self.collection.find_one_and_update(
                filter_query,
                {"$set": update_doc},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )

        doc = await run_db_op(
            self.logger,
            _op,
            success_event=success_event,
            error_event=error_event,
            context=context,
        )
        return self.db_model.model_validate(doc)
