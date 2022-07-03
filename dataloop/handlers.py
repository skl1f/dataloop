from dataclasses import asdict
from aio_pika import Message as RMQMessage
from aio_pika.exceptions import QueueEmpty
from aiohttp import web
from bson import ObjectId
from bson.json_util import dumps
from dataloop.model import Message, MongoRequest


async def mongo_get_handler(request):
    try:
        payload = MongoRequest(**await request.json())
        if payload.id != '':
            result = await request.app['messages'].find_one({'_id': ObjectId(payload.id)})
        else:
            result = request.app['messages'].find({})
            result = await result.to_list(length=100)
        return web.json_response(text=dumps(result))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def handle(request):
    return web.Response(text="Hello")


async def mongo_put_handler(request):
    try:
        payload = Message(**await request.json())
        result = await request.app['messages'].insert_one(asdict(payload))
        return web.json_response(text=dumps({'id': str(result.inserted_id)}))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def mongo_delete_handler(request):
    try:
        payload = MongoRequest(**await request.json())
        result = await request.app['messages'].delete_one({'_id': ObjectId(payload.id)})
        return web.json_response(text=dumps(result.raw_result))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def mongo_list_databases(request):
    try:
        result = await request.app['mongo'].list_databases()
        result = await result.to_list(length=100)
        return web.json_response(text=dumps(result))
    except Exception as e:
        return web.json_response({'msg': repr(e)})


async def rabbitmq_get_handler(request):
    try:
        response = await request.app['queue'].get()
    except QueueEmpty:
        return web.json_response({'warning': 'queue is empty'})
    await response.ack()
    return web.json_response({'msg': response.body.decode()})


async def rabbitmq_put_handler(request):
    try:
        payload = Message(**await request.json())
        await request.app['channel'].default_exchange.publish(
            RMQMessage(bytes(str(payload), 'utf-8')),
            routing_key=request.app['queue'].name,
        )
        return web.json_response({'msg': 'delivered'})
    except Exception as e:
        return web.json_response({'msg': repr(e)})
