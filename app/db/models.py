from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger, Integer, String, ForeignKey

from app.db.database import Base

class User(Base):
	__tablename__ = 'users'

	id: Mapped[int] = mapped_column(primary_key=True)
	telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True) 
	websites: Mapped[list['Website']] = relationship(back_populates='user')

class Website(Base):
	__tablename__ = 'websites'
	
	id: Mapped[int] = mapped_column(primary_key=True)
	url: Mapped[str] = mapped_column(String(255), nullable=False)
	user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
	user: Mapped['User'] = relationship(back_populates='websites')