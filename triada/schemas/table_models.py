from pydantic import ConfigDict
from datetime import datetime, timedelta
from sqlalchemy import Column, Interval
from sqlmodel import SQLModel, Field

class Battles(SQLModel, table=True):
    __tablename__ = "battles"

    link: int = Field(primary_key=True)
    date: datetime = Field(default=datetime.now())
    status: str = Field(default="active")
    judge_id: int
    turn: int = Field(default=0)
    time_out: timedelta

    model_config = ConfigDict(extra='forbid')


class Users(SQLModel, table=True):
    __tablename__ = "users"

    user_id: int = Field(primary_key=True)
    user_name: str
    wins: int = Field(default=0)
    technical_wins: int = Field(default=0)
    loses: int = Field(default=0)
    technical_loses: int = Field(default=0)
    mmr: int = Field(default=100)
    fragments_of_victories: int = Field(default=0)
    fragments_of_greatness: int = Field(default=0)
    skill_rating: int = Field(default=0)


    model_config = ConfigDict(extra='forbid')


class BattlesPlayers(SQLModel, table=True):
    __tablename__ = "battles_players"

    id: int = Field(default=None, primary_key=True)
    user_id: int
    character: str
    universe: str
    turn: int
    result: str | None = Field(default=None)
    time_out: datetime | None = Field(default=None)  # Сопоставляем с INTERVAL
    user_name: str
    hidden_action: str | None
    link: int

    model_config = ConfigDict(extra='forbid')


class Judges(SQLModel, table=True):
    __tablename__ = "juddes"

    judge_id: int = Field(primary_key=True)
    total_ratings: int = Field(default=0)
    rating: int = Field(default=5)
    closed_battles: int = Field(default=0)
    active_battles: int = Field(default=0)

    model_config = ConfigDict(extra='forbid')


class Ratings(SQLModel, table=True):
    __tablename__ = "ratings"

    id: int = Field(default=None, primary_key=True)
    user_id: int
    judge_id: int
    judge_score: int = Field(default=None)
    user_score: int = Field(default=None)

    model_config = ConfigDict(extra='forbid')

