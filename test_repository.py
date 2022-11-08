import pytest

import model
import repository
from orm import order_lines, batches, allocations
from test_orm import postgres_session, postgres_db


def test_repository_can_save_a_batch(postgres_session):
    batch = model.Batch('batch1', "RUSTY_SOAPDISH", 100, eta=None)
    repo = repository.SqlAlchemyRepository(postgres_session)
    repo.add(batch)
    rows = repo.list()
    assert rows == [batch]


def test_fake_repository_can_save_a_batch():
    batch = model.Batch('batch', "RUSTY_SOAPDISH", 100, eta=None)
    batch1 = model.Batch('batch1', "BOHEM_RAPSODY", 10, eta=None)

    repo = repository.FakeRepository([batch])
    repo.add(batch1)

    saved_batch = repo.get('batch1')
    assert saved_batch == batch1


def insert_order_lines(postgres_session) -> int:
    order = model.OrderLine('order1', 'ROUND-TABLE', 12)
    postgres_session.add(order)

    orderline = postgres_session.query(model.OrderLine).filter(model.OrderLine.orderid == 'order1',
                                                               model.OrderLine.sku == 'ROUND-TABLE').one()

    return orderline.id


def insert_batch(postgres_session, reference: str, qty: int) -> int:
    batch = model.Batch(reference, 'ROUND-TABLE', qty, None)
    postgres_session.add(batch)

    order_batch = postgres_session.query(model.Batch).filter(model.Batch.reference == reference).one()
    return order_batch.id


def insert_allocation(postgres_session, orderline_id: int, batch_id: int):
    # I think we should use model.allocate instead raw request, but this is showing how our entity mapped via sqlalchemy
    postgres_session.execute(f'''INSERT INTO {allocations} (orderline_id, batch_id) 
                                 VALUES ({orderline_id}, {batch_id});''')


def test_repository_can_retrive_a_batch_with_allocations(postgres_session):
    orderline_id = insert_order_lines(postgres_session)
    batch1_id = insert_batch(postgres_session, 'batch1', 100)
    insert_batch(postgres_session, 'batch2', 10)
    insert_allocation(postgres_session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(postgres_session)
    retrived = repo.get('batch1')

    expected = model.Batch('batch1', 'ROUND-TABLE', 100, None)

    assert retrived == expected
    assert retrived.sku == expected.sku
    assert retrived._purchased_quantity == expected._purchased_quantity
    assert retrived._allocations == {model.OrderLine('order1', 'ROUND-TABLE', 12)}
