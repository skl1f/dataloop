import os
import sys
from dataclasses import asdict

import motor.motor_asyncio
from aio_pika.exceptions import QueueEmpty
from aiohttp import web
from bson import ObjectId
from bson.json_util import dumps
from motor.frameworks import asyncio
from pydantic.dataclasses import dataclass, Optional
import motor.motor_asyncio
from aio_pika import Message as RMQMessage, connect
import motor.motor_asyncio
from pymongo.errors import CollectionInvalid


async def create_mongo_connection(app):
    conn_str = f"mongodb+srv://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@" \
               f"{os.environ['MONGODB_HOSTNAME']}/?retryWrites=true&w=majority"
    app['mongo'] = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    app['database'] = app['mongo']['dataloop']
    app['messages'] = app['database']['messages']
    await initialize_database(app)


async def initialize_database(app):
    try:
        await app['database'].create_collection("messages")
    except CollectionInvalid as e:
        print(e)
        pass
    except Exception as e:
        print(e)
        sys.exit(1)


async def dispose_mongo_connection(app):
    app['mongo'].close()

async def create_rabbitmq_connection(app):
    conn_str = f"amqps://{os.environ['RABBITMQ_USERNAME']}:{os.environ['RABBITMQ_PASSWORD']}@" \
               f"{os.environ['RABBITMQ_HOSTNAME']}/{os.environ['RABBITMQ_USERNAME']}"
    app['rabbitmq'] = await connect(conn_str)
    app['channel'] = await app['rabbitmq'].channel()
    app['queue'] = await app['channel'].declare_queue("messages")


async def dispose_rabbitmq_connection(app):
    await app['rabbitmq'].close()

async def create_mongo_connection(app):
    conn_str = f"mongodb+srv://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@" \
               f"{os.environ['MONGODB_HOSTNAME']}/?retryWrites=true&w=majority"
    app['mongo'] = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    app['database'] = app['mongo']['dataloop']
    app['messages'] = app['database']['messages']
    await initialize_database(app)


async def initialize_database(app):
    try:
        await app['database'].create_collection("messages")
    except CollectionInvalid as e:
        print(e)
        pass
    except Exception as e:
        print(e)
        sys.exit(1)


async def dispose_mongo_connection(app):
    app['mongo'].close()


@dataclass
class Message:
    key: str
    value: str


@dataclass
class MongoRequest:
    id: Optional[str] = ""


async def handle(request):
    text = "Hello"
    return web.Response(text=text)


async def mongo_get_handler(request):
    try:
        payload = MongoRequest(**await request.json())
        if payload.id != '':
            result = await app['messages'].find_one({'_id': ObjectId(payload.id)})
        else:
            result = app['messages'].find({})
            result = await result.to_list(length=100)
        return web.json_response(text=dumps(result))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def mongo_put_handler(request):
    try:
        payload = Message(**await request.json())
        result = await app['messages'].insert_one(asdict(payload))
        return web.json_response(text=dumps({'id': str(result.inserted_id)}))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def mongo_delete_handler(request):
    try:
        payload = MongoRequest(**await request.json())
        result = await app['messages'].delete_one({'_id': ObjectId(payload.id)})
        return web.json_response(text=dumps(result.raw_result))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def mongo_list_databases(request):
    try:
        db = app['mongo']
        result = await db.list_databases()
        result = await result.to_list(length=100)
        return web.json_response(text=dumps(result))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def rabbitmq_get_handler(request):
    try:
        response = await app['queue'].get()
    except QueueEmpty:
        return web.json_response({'warning': 'queue is empty'})
    await response.ack()
    return web.json_response({'msg': response.body.decode()})


async def rabbitmq_put_handler(request):
    try:
        payload = Message(**await request.json())
        await app['channel'].default_exchange.publish(
            RMQMessage(bytes(str(payload), 'utf-8')),
            routing_key=app['queue'].name,
        )
        return web.json_response({'msg': 'delivered'})
    except Exception as e:
        return web.json_response({'msg': repr(e)})


app = web.Application()
app.on_startup.append(create_mongo_connection)
app.on_cleanup.append(dispose_mongo_connection)
app.on_startup.append(create_rabbitmq_connection)
app.on_cleanup.append(dispose_rabbitmq_connection)

app.add_routes([web.get('/', handle),
                web.get('/mongo', mongo_get_handler),
                web.put('/mongo', mongo_put_handler),
                web.delete('/mongo', mongo_delete_handler),
                web.get('/mongo/list_databases', mongo_list_databases),
                web.get('/rabbitmq', rabbitmq_get_handler),
                web.put('/rabbitmq', rabbitmq_put_handler)])

if __name__ == '__main__':
    web.run_app(app)
