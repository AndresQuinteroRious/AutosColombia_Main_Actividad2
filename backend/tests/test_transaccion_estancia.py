import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.estancia import transaccion


@pytest.mark.parametrize('transaccion_previa', [False, True])
def test_consulta_con_y_sin_transaccion_previa(transaccion_previa):
    class Consulta:
        def __init__(self, session: Session) -> None:
            self.session = session

        @transaccion
        def consultar(self) -> int:
            return self.session.scalar(text('SELECT 1'))

    engine = create_engine('sqlite://')
    with Session(engine) as session:
        if transaccion_previa:
            session.execute(text('SELECT 1'))
        assert Consulta(session).consultar() == 1
        assert session.in_transaction() == transaccion_previa
    engine.dispose()
