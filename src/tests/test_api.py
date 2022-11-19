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


def random_sku(name: Optional[str] = None):
    return str(uuid.uuid3(NAMESPACE_DNS, name)) if name else uuid.uuid1()


def random_batchref(num: int):
    return str(uuid.UUID(int=num))


def random_orderid():
    return str(uuid.uuid1())


def add_stock(batches: list, postgres_session):
    repo = SqlAlchemyRepository(postgres_session)
    for data in batches:
        batch = model.Batch(*data)
        repo.add(batch)
