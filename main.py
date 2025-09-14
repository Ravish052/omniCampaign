from datetime import datetime
from random import randint
from fastapi import FastAPI, HTTPException, Response
from typing import Any

app = FastAPI(root_path="/api/v1")

@app.get("/")
async def root():
    return {"message": "Hello World"}

data : Any = [
    {
        "campaign_id": 1,
        "name": "summer launch",
        "due_date": datetime.now(),
        "created_at": datetime.now(),
    }, 
    {
        "campaign_id": 2,
        "name": "black friday",
        "due_date": datetime.now(),
        "created_at": datetime.now(),}
]

@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns": data}

@app.get("/campaigns/{campaign_id}")
async def read_campaign(campaign_id: int):
    for campaign in data:
        if campaign["campaign_id"] == campaign_id:
            return {"campaign": campaign}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.post('/campaigns', status_code=201)
async def create_campaign(body : dict[str, Any]):

    new:Any = {
        "campaign_id": randint(100, 1000),
        "name": body.get("name"),
        "due_date": body.get("due_date"),
        "created_at": datetime.now(),
    }

    data.append(new)
    return {"campaign": new}

@app.put("/campaigns/{campaign_id}")
async def delete_campaign( body: dict[str, Any]):
    for index, campaign in enumerate(data):
        if(campaign.get("campaign_id") == body.get("campaign_id")):
            updated: Any = {
                "campaign_id": body.get("campaign_id"),
                "name": body.get("name"),
                "due_date": body.get("due_date"),
                "created_at": campaign.get("created_at"),
            }
            data[index] = updated
            return {"campaign": updated}
    raise HTTPException(status_code=404, detail="Campaign not found")


@app.delete("/campaigns/{campaign_id}")
async def update_campaign( campaign_id: int):
    for index, campaign in enumerate(data):
        if(campaign.get("campaign_id") == "campaign_id"):
            
            data.pop(index)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail="Campaign not found")

