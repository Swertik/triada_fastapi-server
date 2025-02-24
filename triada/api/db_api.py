from sqlmodel import SQLModel, create_engine, Session, Field, select
from triada.config.settings import DATABASE_URL
from datetime import datetime


engine = create_engine(DATABASE_URL, echo=True)  # echo=True для отладки SQL-запросов


class Battles(SQLModel, table=True):
    __tablename__ = "battles"

    link: int = Field(default=None, primary_key=True)
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


# Функция для получения сессии базы данных
def get_session():
    with Session(engine) as session:
        yield session


def get_battle(session: Session, link: int = None, judge_id: int = None, status: str = None):
    if isinstance(link, int):
        print(link)
        return session.get(Battles, link)
    if isinstance(judge_id, int):
        return session.exec(select(Battles).where(Battles.judge_id == judge_id)).all()
    elif isinstance(status, str):
        return session.exec(select(Battles).where(Battles.status == status)).all()
    else:
        return session.exec(select(Battles)).all()


def get_user(session: Session, user_id: int):
    return session.get(Users, user_id)


# Функция для инициализации базы данных (если нужно)
def init_db():
    # Создаст таблицы, если они еще не существуют
    # Если таблицы уже созданы, это не вызовет ошибку
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    with Session(engine) as session:
        # Получение пользователя
        battle = get_battle(session, status="active")
        user = get_user(session, 253900432)
        print(battle)
        print(user)