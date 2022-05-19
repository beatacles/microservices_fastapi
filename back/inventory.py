from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel
import settings

app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins = ['http://localhost:3000'],
                   allow_methods = ['*'],
                   allow_headers = ['*'],
                   )

redis = get_redis_connection(
    host = settings.HOST,
    port = settings.PORT,
    password = settings.PASSWORD,
    decode_responses = True
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        # Коннектор?
        database = redis


@app.get("/products")
def all_pks():
    return Product.all_pks()


@app.post("/products")
def create(product: Product):
    return product.save()


def format(pk: str):
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity,
    }


@app.get("/products/{pk}")
def get(pk: str):
    return Product.get(pk)


@app.delete("/products/{pk}")
def get(pk: str):
    product = Product.get(pk)
    return product.delete(pk)
