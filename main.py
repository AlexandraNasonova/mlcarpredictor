from fastapi import FastAPI, UploadFile, Request
import pandas as pd
from typing import List
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from predictor import Predictor
from pydantic import BaseModel
import datetime
import json

app = FastAPI()
templates = Jinja2Templates(directory='templates')


class CarModel(BaseModel):
    name: str
    year: int
    selling_price: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: str
    seats: float


def convert_list_to_data_frame(items: List[CarModel]) -> pd.DataFrame:
    return pd.DataFrame([vars(y) for y in items])


def convert_data_frame_to_list(items: List[CarModel]) -> pd.DataFrame:
    return pd.DataFrame([vars(y) for y in items])


@app.post("/predict_item_form")
async def predict_item_form(car_json: Request):
    car_json_p = await car_json.json()
    car_dict = json.loads(car_json_p)
    car = CarModel(**car_dict)
    df = convert_list_to_data_frame([car])
    prices = Predictor.predict(df)
    return prices[0]


@app.post("/predict_item")
async def predict_item(car: CarModel):
    df = convert_list_to_data_frame([car])
    prices = Predictor.predict(df)
    return prices[0]


@app.post("/upload_predict_items", response_class=FileResponse)
async def predict_items_csv(file: UploadFile):
    df = pd.read_csv(file.file)
    file.file.close()
    df['selling_price'] = Predictor.predict(df)
    filename = f"./responses_csv/dataset_{str(datetime.datetime.now())}.csv"
    df.to_csv(filename)
    return filename


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

