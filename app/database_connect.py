import os

import motor.motor_asyncio

uri = f"mongodb+srv://{os.getenv('MONGO_USR')}:{os.getenv('MONGO_PWD')}@{os.getenv('MONGO_URL')}/?retryWrites=true&w=majority"
db = motor.motor_asyncio.AsyncIOMotorClient(uri)["comic-back"]
