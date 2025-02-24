from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field
from triada.config.settings import DATABASE_URL

class Message(BaseModel):
    id: int
    text: str
    peer_id: int
    from_id: int
    attachments: Optional[List[dict]] = Field(default=None)
    date: datetime


class BattleCreate(BaseModel):
    link: int
    judge_id: int
    status: str = Field(default="active") 


class Battles(SQLModel, table=True):
    __tablename__ = "battles"

    link: int = Field(primary_key=True)
    date: datetime = Field(default=datetime.now())
    status: str = Field(default="active")
    judge_id: int
    turn: int = Field(default=0)
    time_out: int


class Users(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int = Field(default=None, primary_key=True)
    wins: int = Field(default=0)
    technical_wins: int = Field(default=0)
    loses: int = Field(default=0)
    technical_loses: int = Field(default=0)
    mmr: int = Field(default=100)
    fragments_of_victories: int = Field(default=0)
    fragments_of_greatness: int = Field(default=0)
    skill_rating: int = Field(default=0)
    user_name: str


class BattlesPlayers(SQLModel, table=True):
    __tablename__ = "battles_players"

    id: int = Field(default=None, primary_key=True)
    user_id: int
    character: str
    universe: str
    turn: int
    result: str
    time_out: datetime
    user_name: str
    hidden_action: str
    link: int
