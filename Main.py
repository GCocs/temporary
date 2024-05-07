# -*- coding: utf-8 -*-
from typing import Union
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from nearbyBusstopExample import findBus

app = FastAPI()


class Data(BaseModel):
    destination: str
    pointLati: float
    pointLong: float

@app.post("/find")
def find_round(data: Data):
    return findBus(data.pointLati, data.pointLong, data.destination)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 8080)
