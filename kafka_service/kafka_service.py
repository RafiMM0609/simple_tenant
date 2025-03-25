from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from fastapi import Depends
from models import supabase
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import redis.asyncio as redis
from redis_client import get_redis
import json
from schemas.auth import (
    LoginRequest,
    SignupRequest,
    EditPassRequest,
    MeRequest,
    ListUserRequest,
    )
from routes.auth import (
    login_route,
    regis,
    edit_password,
    list_user,
    me
)
from settings import (
    KAFKA_SERVER,
    KAFKA_TOPIC,
)

# Model Pydantic untuk event
class AuthEvent(BaseModel):
    body: Optional[dict] = None
    param: Optional[dict] = None
    event_type: str 
    timestamp: str

function_dict = {
    "login": login_route,
    "regis": regis,
    "edit-password": edit_password,
    "list-user": list_user,
    "me":me,
}

pdy_dict = {
    "login": LoginRequest,
    "regis": SignupRequest,
    "edit-password": EditPassRequest,
}

pdy_param = {
    "list-user": ListUserRequest,
    "me": MeRequest,
}

# REDIS

async def send_to_redis(event: any, key:str):
    try:
        print("Start send to Redis success")
        redis_conn = await get_redis()  # ✅ Ambil instance Redis langsung
        # pong = await redis_conn.ping()
        # print(f"Redis connection status: {pong}")  # Harus True jika koneksi berhasil
        await redis_conn.set(key, event)
        # print("Send to Redis success")
        return "success"
    except Exception as e:
        raise ValueError(f"Error when sending to Redis: {e}")

# Standrad consumer
async def consumer_events(
    pdymodel: BaseModel,
    pdyparam: BaseModel,
    function: any,
    event_type: str,
):
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        group_id="auth_group"
    )
    await consumer.start()
    try:
        async for message in consumer:
            event_data = json.loads(message.value.decode("utf-8"))
            event = AuthEvent(**event_data)
            print(f"Received event: {event}")
            function = function_dict.get(event.event_type, None)
            pdymodel = pdy_dict.get(event.event_type, None)
            pdyparam = pdy_param.get(event.event_type, None)
            if function is not None:
                if pdymodel is not None:
                    request = pdymodel(**event.body)
                    data = await function(request=request, db=supabase)
                elif pdyparam is not None:
                    params = pdyparam(**event.param)
                    data = await function(**params.dict(), db=supabase)
                elif pdymodel is not None and pdyparam is not None:
                    request = pdymodel(**event.body)
                    params = pdyparam(**event.param)
                    data = await function(**params.dict(), request=request, params=params, db=supabase)
                # data_response = json.loads(data.body.decode("utf-8"))
                event_id=event_data.get("event_id", "unknown")
                try:
                    await send_to_redis(event=data.body.decode("utf-8"), key=event_id)
                except Exception as e:
                    print(e)
            else:
                raise ValueError("Invalid event type, or your forget to regris it to vent dict")
    finally:
        await consumer.stop()

# Consumer 
async def auth_events(
    pdymodel= any,
    pdyparam = any,
    function = login_route,
    event_type = str,
):
    await consumer_events(pdymodel, function, event_type, pdyparam)