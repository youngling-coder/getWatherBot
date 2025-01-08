from sqlalchemy import text, BigInteger, Enum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from custom_types import Units


class User(Base):

    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    units: Mapped[str] = mapped_column(
        Enum(Units),
        nullable=False,
        server_default=text(f"'{Units.metric.value}'"),
        default=Units.metric.value,
    )
