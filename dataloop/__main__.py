import os
import sys
import motor.motor_asyncio
from aiohttp import web
from aio_pika import connect
from pymongo.errors import CollectionInvalid
from dataloop.handlers import mongo_get_handler, handle, mongo_put_handler, mongo_delete_handler, \
    mongo_list_databases, rabbitmq_get_handler, rabbitmq_put_handler


async def create_mongo_connection(config):
    conn_str = f"mongodb+srv://{os.environ['MONGODB_USERNAME']}:{os.environ['MONGODB_PASSWORD']}@" \
               f"{os.environ['MONGODB_HOSTNAME']}/?retryWrites=true&w=majority"
    config['mongo'] = motor.motor_asyncio.AsyncIOMotorClient(conn_str, serverSelectionTimeoutMS=5000)
    config['database'] = config['mongo']['dataloop']
    config['messages'] = config['database']['messages']
    await initialize_database(config)


async def initialize_database(config):
    try:
        await config['database'].create_collection("messages")
    except CollectionInvalid as e:
        print(e)
        pass
    except Exception as e:
        print(e)
        sys.exit(1)


async def dispose_mongo_connection(config):
    config['mongo'].close()


async def create_rabbitmq_connection(config):
    conn_str = f"amqps://{os.environ['RABBITMQ_USERNAME']}:{os.environ['RABBITMQ_PASSWORD']}@" \
               f"{os.environ['RABBITMQ_HOSTNAME']}/{os.environ['RABBITMQ_USERNAME']}"
    config['rabbitmq'] = await connect(conn_str)
    config['channel'] = await config['rabbitmq'].channel()
    config['queue'] = await config['channel'].declare_queue("messages")


async def dispose_rabbitmq_connection(config):
    await config['rabbitmq'].close()


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
