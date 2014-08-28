from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import frapy.settings


Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**frapy.settings.DATABASE))


def create_table(engine):
    Base.metadata.create_all(engine)

class DbForum(Base):
    __tablename__ = "forums"

    id = Column(Integer, primary_key=True)
    domain = Column(String)

class DbCategory(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    title=Column(String)
    url = Column(String)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True) # 0 if no parent
    forum_id = Column(Integer, ForeignKey('forums.id'))

    parent = relationship("DbCategory", uselist=False)
    forum = relationship("DbForum", backref=backref('categories'), order_by=id)

class DbThread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True)
    title=Column(String)
    url = Column(String)
    category_id = Column(Integer, ForeignKey('categories.id'))

    category = relationship("DbCategory", backref=backref('threads'), order_by=id)

class DbPost(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    content = Column(String)
    timestamp = Column(DateTime)
    thread_id = Column(Integer, ForeignKey('threads.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    thread = relationship('DbThread', backref=backref('posts'), order_by=id)
    user = relationship('DbUser', backref=backref('posts'), order_by=id)

class DbUser(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nickname = Column(String)
    name = Column(String, nullable=True)
    join_date = Column(DateTime, nullable=True)
    location = Column(String, nullable=True)
    forum_id = Column(Integer, ForeignKey('forums.id'))

    forum = relationship("DbForum", backref=backref('users'), order_by=id)

