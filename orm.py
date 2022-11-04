from sqlalchemy import Column, Integer, String, Identity, ForeignKey, Table, MetaData, Date
from sqlalchemy.orm import mapper, relationship

import model

metadata = MetaData()

order_lines = 'order_lines'
batches = 'batches'
allocations = 'allocations'

order_lines_table = Table(order_lines, metadata,
                       Column('id', Integer, Identity(start=1), primary_key=True),
                       Column('sku', String(255)),
                       Column('qty', Integer, nullable=False),
                       Column('orderid', String(255)))

batches_table = Table(
    batches,
    metadata,
    Column("id", Integer, Identity(start=1), primary_key=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations_table = Table(
    allocations,
    metadata,
    Column("id", Integer, Identity(start=1), primary_key=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines_table)
    mapper(
        model.Batch,
        batches_table,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations_table,
                collection_class=set,
            )
        },
    )
