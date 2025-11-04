from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException
from typing import Annotated, Any, Generic, TypeVar

from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select

class Campaign(SQLModel, table = True):
    campaign_id: int | None = Field(default = None, primary_key = True)
    name: str= Field(index = True)
    due_date: datetime | None = Field(default = None, index = True)
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc ), nullable =True, index = True)

class CampaignCreate(SQLModel):
    name: str
    due_date: datetime | None = None

sqlite_file_name = 'database.db'
sqlite_url = f'sqlite:///{sqlite_file_name}'

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

sessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name = "Summer Launch", due_date = datetime.now()),
                Campaign(name = "Black Friday", due_date = datetime.now())
                ])
            session.commit()
            
    yield
    
app = FastAPI(root_path="/api/v1", lifespan=lifespan)

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
# class campaignResposne(BaseModel):
#     campaigns: list[Campaign]

T = TypeVar("T")
class Response(BaseModel, Generic[T]):
    data: T
    
@app.get("/campaigns", response_model = Response[list[Campaign]])
async def read_campaigns(session: sessionDep):
    campaigns = session.exec(select(Campaign)).all()
    return {"data": campaigns}

@app.get("/campaigns/{campaign_id}", response_model = Response[Campaign])
async def read_campaign(campaign_id: int, session: sessionDep):
    campaign = session.get(Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"data": campaign}


@app.post('/campaigns', status_code=201, response_model = Response[Campaign])
async def create_campaign(body : CampaignCreate, session: sessionDep):
    # new_campaign = Campaign(name = body.name, due_date = body.due_date)
    db_campaign = Campaign.model_validate(body)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data": db_campaign}

@app.put("/campaigns/{campaign_id}", response_model = Response[Campaign])
async def update_campaign(campaign_id: int, body: CampaignCreate, session: sessionDep):
    data = session.get(Campaign, campaign_id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    data.name = body.name
    data.due_date = body.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data": data}

@app.delete("/campaigns/{campaign_id}", status_code=204)
async def delete_campaign(campaign_id: int, session: sessionDep):
    data = session.get(Campaign, campaign_id)
    if not data:
        raise HTTPException(status_code=404, detail="Campaign not found")
    session.delete(data)
    session.commit()
    return

# @app.get("/campaigns")
# async def read_campaigns():   
#     return {"campaigns": data}

# @app.get("/campaigns/{campaign_id}")
# async def read_campaign(campaign_id: int):
#     for campaign in data:
#         if campaign["campaign_id"] == campaign_id:
#             return {"campaign": campaign}
#     raise HTTPException(status_code=404, detail="Campaign not found")

# @app.post('/campaigns', status_code=201)
# async def create_campaign(body : dict[str, Any]):

#     new:Any = {
#         "campaign_id": randint(100, 1000),
#         "name": body.get("name"),
#         "due_date": body.get("due_date"),
#         "created_at": datetime.now(),
#     }

#     data.append(new)
#     return {"campaign": new}

# @app.put("/campaigns/{campaign_id}")
# async def delete_campaign( body: dict[str, Any]):
#     for index, campaign in enumerate(data):
#         if(campaign.get("campaign_id") == body.get("campaign_id")):
#             updated: Any = {
#                 "campaign_id": body.get("campaign_id"),
#                 "name": body.get("name"),
#                 "due_date": body.get("due_date"),
#                 "created_at": campaign.get("created_at"),
#             }
#             data[index] = updated
#             return {"campaign": updated}
#     raise HTTPException(status_code=404, detail="Campaign not found")


# @app.delete("/campaigns/{campaign_id}")
# async def update_campaign( campaign_id: int):
#     for index, campaign in enumerate(data):
#         if(campaign.get("campaign_id") == "campaign_id"):
            
#             data.pop(index)
#             return Response(status_code=204)
#     raise HTTPException(status_code=404, detail="Campaign not found")



