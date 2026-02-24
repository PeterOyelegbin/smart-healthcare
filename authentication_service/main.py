from fastapi import FastAPI, Depends, Path
from sqlalchemy.orm import Session
from database import models, schema
from database.db_config import get_db

# initialize the application and modify default api details
app = FastAPI(
    title="Authentication Service - FastAPI",
    description="Authentication service for managing user authentication and authorization",
    version="0.0.1",
    # openapi_url="/docs",
    contact={
        "name": "Peter Oyelegbin",
        "email": "peteroyelegbin@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


# get all registered users
@app.get("/api/vi/users")
async def getUsers(session: Session = Depends(get_db)):
    users = session.query(models.User).all()
    if users == []:
        return "No data found"
    else:
        return users
    

# get a user by its id
@app.get("/api/vi/users/{id}")
async def getUser(id:int = Path(..., description="task ID you want to retrieve", gt=0), session: Session = Depends(get_db)):
    user = session.query(models.User).get(id)
    if user is None:
        return "No data found"
    else:
        return user
    

# create a new user
@app.post("/api/v1/users/create")
async def addUser(user:schema.User, session: Session = Depends(get_db)):
    user = models.User(username=user.username, email=user.email, password=user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
