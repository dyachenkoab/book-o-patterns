from sqlalchemy import Column, Integer, String, Identity, ForeignKey, Table, MetaData, Date
from sqlalchemy.orm import mapper, relationship

import model

metadata = MetaData()

table = "order_lines"
order_lines_al = Table(table, metadata,
                    Column('id', Integer, Identity(start=1), primary_key=True),
                    Column('sku', String(255)),
                    Column('qty', Integer, nullable=False),
                    Column('orderid', String(255)))

batches = Table(
    "batches",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("reference", String(255)),
    Column("sku", String(255)),
    Column("_purchased_quantity", Integer, nullable=False),
    Column("eta", Date, nullable=True),
)

allocations = Table(
    "allocations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("orderline_id", ForeignKey("order_lines.id")),
    Column("batch_id", ForeignKey("batches.id")),
)


def start_mappers():
    lines_mapper = mapper(model.OrderLine, order_lines_al)
    mapper(
        model.Batch,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
