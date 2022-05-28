from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.base import Base


class SubDays(Base):
    __tablename__ = "subdays"

    user_id = Column(BigInteger, unique=True, primary_key=True)
    group_id = Column(BigInteger)
    sub_days = Column(Integer, default=0)
    # joined = Column(BigInteger)
    status = Column(String(50), default="left")
