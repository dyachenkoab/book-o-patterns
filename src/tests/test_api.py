from typing import Optional

import pytest
import requests

from src import config
from src.domain import model
from src.tests.test_orm import postgres_session, postgres_db, cleanup_part
from src.adapters.repository import SqlAlchemyRepository
import uuid
from uuid import NAMESPACE_DNS


@pytest.fixture()
def restart_api():
    pass


@pytest.mark.usefixtures('restart_api')
def test_api_returns_allocation(postgres_session):
    sku, othersku = random_sku(), random_sku('other')
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    otherbatch = random_batchref(3)
    add_stock([
        (laterbatch, sku, 100, '2011-01-02'),
        (earlybatch, sku, 100, '2011-01-01'),
        (otherbatch, othersku, 100, None)
    ], postgres_session)
    data = {'orderid': random_orderid(), 'sku': sku, 'qty': 3}
    url = config.get_api_url()
    print(sku, '\n', othersku, '\n', earlybatch, '\n', laterbatch, '\n', otherbatch, '\n', data, '\n', url)
    # r = requests.post(f'{url}/allocate', json=data)
    # assert r.status_code == 201
    # assert r.json()['batchref'] == earlybatch


@pytest.mark.usefixtures('restart_api')
def test_allocations_are_persisted(postgres_session):
    sku = random_sku()
    qty = 10
    batch1, batch2 = random_batchref(1), random_batchref(2)
    order1, order2 = random_orderid(1), random_orderid(2)

    add_stock([
        (batch1, sku, qty, '2011-01-01'),
        (batch2, sku, qty, '2011-01-02')
    ], postgres_session)

    line1 = {'orderid': order1, 'sku': sku, 'qty': qty}
    line2 = {'orderid': order2, 'sku': sku, 'qty': qty}
    url = config.get_api_url()

    # # первый заказ исчерпывает все товары в партии 1
    # r = requests.post(f'{url}/allocate', json=line1)
    # assert r.status_code == 201
    # assert r.json()['batchref'] == batch1
    #
    # # второй заказ должен пойти в портию 2
    # r = requests.post(f'{url}/allocate', json=line2)
    # assert r.status_code == 201
    # assert r.json()['batchref'] == batch2


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_out_of_stock(postgres_session):
    sku, small_batch, large_order = random_sku(), random_batchref(1), random_orderid()
    add_stock([(small_batch, sku, 10, '2011-01-01')], postgres_session)
    data = {'orderid': large_order, 'sku': sku, 'qty': 20}
    url = config.get_api_url()
    # r = requests.post(f'{url}/allocate', json=data)
    # assert r.status_code == 400
    # assert r.json()['message'] == f'Артикула {sku} нет в наличии.'


@pytest.mark.usefixtures('restart_api')
def test_400_message_for_invalid_sku():
    unknown_sku, orderid = random_sku(), random_orderid()
    data = {'orderid': orderid, 'sku': unknown_sku, 'qty': 20}
    url = config.get_api_url()
    # r = requests.post(f'{url}/allocate', json=data)
    # assert r.status_code == 400
    # assert r.json()['message'] == f'Недопустимый артикул {unknown_sku}'


def random_sku(name: Optional[str] = None):
    return str(uuid.uuid3(NAMESPACE_DNS, name)) if name else str(uuid.uuid1())


def random_batchref(num: int):
    return str(uuid.UUID(int=num))


def random_orderid(num: Optional[int] = None):
    # Алгоритм совпадает с random_batchref(), правильно ли это?
    return str(uuid.UUID(int=num)) if num else str(uuid.uuid1())


def add_stock(batches: list, session):
    repo = SqlAlchemyRepository(session)
    for data in batches:
        batch = model.Batch(*data)
        repo.add(batch)
