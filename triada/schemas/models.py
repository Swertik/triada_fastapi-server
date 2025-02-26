from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field


class Message(BaseModel):
    id: int
    text: str
    peer_id: int
    from_id: int
    attachments: Optional[List[dict]] = Field(default=None)
    date: datetime

    model_config = ConfigDict(extra='forbid')


class Battles(SQLModel, table=True):
    __tablename__ = "battles"

    link: int = Field(primary_key=True)
    date: datetime = Field(default=datetime.now())
    status: str = Field(default="active")
    judge_id: int
    turn: int = Field(default=0)
    time_out: int

    model_config = ConfigDict(extra='forbid')


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

    model_config = ConfigDict(extra='forbid')


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

    model_config = ConfigDict(extra='forbid')
