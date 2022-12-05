import os

import motor.motor_asyncio

uri = f"mongodb+srv://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PWD')}@{os.getenv('MONGO_URL')}/authMechanism=DEFAULT&retryWrites=true&w=majority"
# uri = f"mongodb://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PWD')}@{os.getenv('MONGO_URL')}/authMechanism=DEFAULT&retryWrites=true&w=majority&authSource=comic-back"
db = motor.motor_asyncio.AsyncIOMotorClient(uri)["comic-back"]
