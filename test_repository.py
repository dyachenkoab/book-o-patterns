import model
import repository


def test_repository_can_save_a_batch(session):
    batch = model.Batch('batch1', "RUSTY_SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = list(session.execute('SELECT reference, sku, _purchased_quantity, eta FROM "batches"'))
    assert rows == [('batch1', "RUSTY_SOAPDISH", 100, None)]


def test_fake_repository_can_save_a_batch():
    batch = model.Batch('batch', "RUSTY_SOAPDISH", 100, eta=None)
    batch1 = model.Batch('batch1', "BOHEM_RAPSODY", 10, eta=None)

    repo = repository.FakeRepository([batch])
    repo.add(batch1)

    saved_batch = repo.get('batch1')
    assert saved_batch == batch1

