import abc

import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(model.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(model.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self.__batches = set(batches)

    def add(self, batch):
        self.__batches.add(batch)

    def get(self, reference) -> model.Batch:
        try:
            return next(b for b in self.__batches if b.reference == reference)
        except StopIteration:
            print('Batch did not found.')

    def list(self):
        return list(self.__batches)
