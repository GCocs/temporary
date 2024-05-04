# -*- coding: utf-8 -*-
from typing import Union
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Data(BaseModel):
    destination: str
    pointLati: float
    pointLong: float

@app.post("/find")
def find_round(data: Data):
    print(data)
    return data


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 8080)
