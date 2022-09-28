from bson import ObjectId

from app.database_connect import db
from app.services import Collections


async def search_by_id(object_id: str, collection: Collections):
    return await db[collection.value].find_one({"_id": ObjectId(object_id)})


async def update_by_id(object_id: str, collection: Collections, dict_data: {}):
    return await db[collection.value].update_one({"_id": ObjectId(object_id)}, {"$set": dict_data})


async def insert_one(collection: Collections, dict_data: {}):
    return await db[collection.value].insert_one(dict_data)


async def get_list(collection: Collections):
    return await db[collection.value].find().to_list(None)


async def delete_by_id(object_id: str, collection: Collections):
    return await db[collection.value].delete_one({"_id": ObjectId(object_id)})


async def search_with_attributes(attributes: {}, collection: Collections):
    return await db[collection.value].find_one(attributes)


async def search_many_with_attributes(attributes: {}, collection: Collections):
    return await db[collection.value].find(attributes).to_list(None)
