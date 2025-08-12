import os
from sqlalchemy import create_engine, Column, Integer, Float, Text, Date, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import date

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///trainer_payout.db")
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    split_trainer = Column(Float, default=0.70)
    split_gym = Column(Float, default=0.30)
    agreements = relationship("Agreement", back_populates="trainer")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    agreements = relationship("Agreement", back_populates="client")

class Agreement(Base):
    __tablename__ = "agreements"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    session_length_min = Column(Integer, default=60)
    price_per_session = Column(Float, nullable=False)
    client = relationship("Client", back_populates="agreements")
    trainer = relationship("Trainer", back_populates="agreements")

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    trainer_id = Column(Integer, ForeignKey("trainers.id"))
    client_id = Column(Integer, ForeignKey("clients.id"))
    session_length_min = Column(Integer, default=60)
    price_per_session = Column(Float, nullable=False)
    attended = Column(Integer, default=1)
    notes = Column(Text, default="")

class Config(Base):
    __tablename__ = "config"
    id = Column(Integer, primary_key=True)
    key = Column(Text, unique=True)
    value = Column(Text)

def init_db(seed: bool = True):
    Base.metadata.create_all(bind=engine)
    if not seed:
        return
    with SessionLocal() as s:
        if s.query(Trainer).first():
            return
        t1 = Trainer(name="Ava Martinez", split_trainer=0.70, split_gym=0.30)
        t2 = Trainer(name="Jordan Lee",   split_trainer=0.70, split_gym=0.30)
        t3 = Trainer(name="Chris Patel",  split_trainer=0.70, split_gym=0.30)
        s.add_all([t1, t2, t3])
        c1 = Client(name="Taylor Reed")
        c2 = Client(name="Morgan Chen")
        c3 = Client(name="Sam Rivera")
        c4 = Client(name="Jamie Fox")
        c5 = Client(name="Alex Johnson")
        s.add_all([c1, c2, c3, c4, c5])
        s.flush()
        s.add_all([
            Agreement(client_id=c1.id, trainer_id=t1.id, start_date=date(date.today().year,1,10), session_length_min=60, price_per_session=80.0),
            Agreement(client_id=c2.id, trainer_id=t1.id, start_date=date(date.today().year,3,2),  session_length_min=60, price_per_session=75.0),
            Agreement(client_id=c3.id, trainer_id=t2.id, start_date=date(date.today().year,2,15), session_length_min=45, price_per_session=70.0),
            Agreement(client_id=c4.id, trainer_id=t2.id, start_date=date(date.today().year,5,1),  session_length_min=60, price_per_session=90.0),
            Agreement(client_id=c5.id, trainer_id=t3.id, start_date=date(date.today().year,4,20), session_length_min=60, price_per_session=85.0),
        ])
        s.add_all([
            Config(key="projection_months_ahead", value="6"),
            Config(key="default_retention_rate", value="0.92"),
            Config(key="default_growth_rate", value="0.05"),
        ])
        s.commit()
