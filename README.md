# FastAPI Beyond CRUD
This talk is going to show you fastapi concepts beyond CRUD. But it will start with a simple app. (CRUD) app.

## The simple CRUD APP
this is gonna be a simple CRUD app for comments on this specific talk. How it works is that you ( the audience) will type your comments, they will be saved and shown in real time for all of us to see. (keep it Pycon please.)

## Let us start with a simple database model and server in a singular web app
we shall create that using [SQLModel](https://sqlmodel.tiangolo.com), a simple ORM based on the popular SQLAlchemy ORM.

## Installation
We shall install it with 
```python
pip install fastapi[standard] sqlmodel
```
## Creating a Database Model
let us create a simple file `app.py` where we can add a very simple database model.


```python
from sqlmodel import SQLModel, Field, Index
from typing import Optional
from datetime import datetime, timezone


class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_ip: str = Field(max_length=45, nullable=False)  # Supports IPv4 and IPv6
    comment_text: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=datetime.now(tz=timezone.utc), sa_column_kwargs={"onupdate": datetime.now(tz=timezone.utc)})

    __table_args__ = (
        Index("idx_talk_id", "talk_id"),
        Index("idx_user_ip", "user_ip"),
    )
```

## Creating the database

let us create that table in a database

```python
from sqlmodel import create_engine

# ... the model
engine = create_engine("sqlite:///comments.db")

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
```

Run that file normally with

```bash
python3 app.py
```

The tables are created, let us create a database table using the model.
![database table created](./img/1.png)


# Validation with Pydantic
Now that the tables are created, let us do some CRUD. (Your app is a CRUD app)

```python
# .. other imports
from pydantic import BaseModel

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # ... the rest of the fields 
    # we shall use this as a read schema (sqlmodel)

class CommentCreateSchema(BaseModel):
    user_ip : str = Field(max_length=45)
    comment_text: str

class CommentUpdateSchema(BaseModel):
    comment_text: str
```

All these are still in the `app.py` file. Let us now create the FastAPI instance. 

```python
# ... other imports
from fastapi import FastAPI

app  = FastAPI()

```

Now what we need is a `session` object because that is what SQLModel requires us to do any CRUD. We shall create a **dependency** . let us do that here

```python
from sqlmodel import Session

engine = create_engine("sqlite:///comments.db")

def get_session():
    with Session(engine) as session:
        yield session
```

This will be injected into every path handler we shall implement. Lastly, let us create the CRUD.

## Read and Create Endpoints
```python

# ... the rest of the code

@app.post("/comments/", response_model=CommentResponse)
def create_comment(
    comment: CommentCreateSchema, session: Session = Depends(get_session)
):
    """Create a new comment."""
    db_comment = Comment(**comment.model_config())
    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


@app.get("/comments/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: int, session: Session = Depends(get_session)):
    """Read a comment by ID."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@app.get("/comments/ip/{user_ip}", response_model=List[CommentResponse])
def read_comments_by_ip(user_ip: str, session: Session = Depends(get_session)):
    """Read all comments by user IP."""
    statement = select(Comment).where(Comment.user_ip == user_ip)
    comments = session.exec(statement).all()
    return comments

```
## Update and Delete Endpoints
```python
# ... the rest of the code
@app.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdateSchema,
    session: Session = Depends(get_session),
):
    """Update a comment's text, talk_id, or user_ip."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    # Verify talk exists
    comment.comment_text = comment_update.comment_text
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@app.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, session: Session = Depends(get_session)):
    """Delete a comment."""
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    session.delete(comment)
    session.commit()
    return {"message": "Comment deleted"}
```

## Running the App
Running the application is simple and can be done with
```
fastapi dev
``` 

Done. Test this with your API Client of choice. But we can use the Swagger UI documentation that ships by default.

![Swagger](./img/2.png)

## What is next after CRUD? (Beyond CRUD)
- A better Project Structure
- Decoupling Settings (Config)
- Advanced Dependency Injection
- Authentication

## A better Structure with routers,
begin the work of restruiring the project from 

```
── app.py
└── comments.db
```

a better one with routers


```
├── api
│   ├── auth
│   │   ├── constants.py
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── comments
│   │   ├── constants.py
│   │   ├── dependencies.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── services.py
│   └── __init__.py
├── app.py
├── config.py
└── site.db
```
let each entity in your app have a folder of its own with routes, schemas, models and so on. separate each concern.

### How to do that?
we can utitlize the `APIRouter` class to help us group related endpoints on our application.
```python

from fastapi import APIRouter

comments_router = APIRouter(
    prefix="/comments",
    tags=['comments']
)

@comment_router.get("/", response_model=List[CommentResponse])
def read_comments_by_talk(session: Session = Depends(get_session)):
    """Read all comments for a talk."""
    ...
@comment_router.post("/", response_model=CommentResponse)
def create_comment(
    comment: CommentCreateSchema, session: Session = Depends(get_session)
):
    """Create a new comment."""
    ...

@comment_router.get("/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: int, session: Session = Depends(get_session)):
    """Read a comment by ID."""
    ...


@comment_router.get("/ip/{user_ip}", response_model=List[CommentResponse])
def read_comments_by_ip(user_ip: str, session: Session = Depends(get_session)):
    """Read all comments by user IP."""
    ...
    
```

Register your related endpoints onto the FastAPI app instance by doing the following.

```python
# ... the rest of the imports
from  api.comments.routes import comment_router
from api.auth.routes import auth_router

app = FastAPI(
    title="LiveTalk API V1",
    description="A simple REST API built for a talk at Pycon Uganda 2025"
)


app.include_router(router=comment_router)
aoo.include_router(router=auth_router)
# ... rest of the routers

```


Put your schemas inside the folder specific `schemas.py` file to make things organized

```python
# inside api/comments/schemas.py

from pydantic import BaseModel, Field

class CommentCreateSchema(BaseModel):
    user_ip: str = Field(max_length=45)
    comment_text: str


class CommentUpdateSchema(BaseModel):
    comment_text: str

```

Create service files to organize module specific logic 

```python
from sqlmodel import Session, select

async def read_all_comments(session:Session):
    """Read all comments for a talk."""
    statement = select(Comment).where(Comment.talk_id == talk_id)
    result = session.exec(statement).all()
    return result

async def create_comment(session:Session):
    # .... the rest of the code

```