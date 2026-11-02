# models.py
class Cuenta(Base):
    __tablename__ = "cuenta"
    id = Column(BigInteger, primary_key=True)
    usuario = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    rol = Column(Text, nullable=False)
    operador_id = Column(BigInteger, ForeignKey("operador.id"), nullable=True)
    