import model
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from orm import start_mappers, table, metadata


@pytest.fixture
def postgres_db():
    engine = create_engine('postgresql://postgres@127.0.0.1/postgres')
    engine.connect()
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


def test_orderline_mapper_can_load_lines(postgres_session):
    postgres_session.execute(
        f'''INSERT INTO {table} (ORDERID, SKU, QTY) VALUES
        ('order1', 'RED-CHAIR', 12),
        ('order1', 'COUNTRY-LAMP', 13),
        ('order2', 'BLUE-LIPSTICK', 14);''')

    expected = [
        model.OrderLine("order1", 'RED-CHAIR', 12),
        model.OrderLine("order1", 'COUNTRY-LAMP', 13),
        model.OrderLine("order2", 'BLUE-LIPSTICK', 14),
    ]

    assert postgres_session.query(model.OrderLine).all() == expected
