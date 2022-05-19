from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from starlette.requests import Request
import settings
import requests
import time

app = FastAPI()
app.add_middleware(CORSMiddleware,
               allow_origins = ['http://localhost:3000'],
               allow_methods = ['*'],
               allow_headers = ['*'],
               )

# This should be a different database
redis = get_redis_connection(
    host = settings.HOST,
    port = settings.PORT,
    password = settings.PASSWORD,
    decode_responses = True,
)
@app.get ('/orders/{pk}')
def get(pk: str):

    return Order.get(pk)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str #pending, completed, refunded

    class Meta:
        database = redis
@app.post("/orders")
async def create(request: Request, background_task: BackgroundTasks):
    body = await request.json() # id, quantity
    req = requests.get("http://localhost:8000/products/%s" % body["id"])
    product =  req.json()

    order = Order(
        product_id = body['id'],
        price = product['price'],
        fee = 0.2 * product['price'],
        total = 1.2 * product['price'],
        quantity = body['quantity'],
        status = 'pending'
    )
    order.save()
    background_task.add_task(order_completed, order)

    return order

def order_completed(order: Order):
    time.sleep(3)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*', )# auto-generated id - *
