from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import sessionmaker


engine = create_engine("sqlite+pysqlite:///quiz-tg-bot.sqlite3", echo=True, future=True)
Base = declarative_base()


def getSession():
    Session = sessionmaker(bind=engine)
    session = Session()

    return session


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True, index=True, nullable=False)

    tg_id = Column(Text, nullable=False, unique=True)
    task_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)


    created = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)


def start_db():
    Base.metadata.create_all(engine)


def _add(some):
    session = getSession()

    session.add(some)
    session.commit()

    session.close()


def createUser(tg_id):
    d = datetime.now()

    user = User(tg_id=str(tg_id), task_id=0, score=0, created=d, updated=d)

    _add(user)

    return user


def getUser(tg_id):
    session = getSession()
    response = session.query(User).filter_by(tg_id=tg_id).first()

    session.close()

    return response


def update(some):
    some.updated = datetime.now()
    _add(some)


def main():
    start_db()


if __name__ == '__main__':
    main()
