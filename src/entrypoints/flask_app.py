from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src import config
from src.domain import model
from src.adapters import orm, repository

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route('/allocate', methods=['POST'])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(request.json['orderid'],
                           request.json['sku'],
                           request.json['qty'])

    batchref = model.allocate(line, batches)

    if not is_valid_sku(line.sku, batches):
        return jsonify({'message': f'Недопустимый артикул {line.sku}'}), 400

    try:
        batchref = model.allocate(line, batches)
    except model.OutOfStock as e:
        return jsonify({'message': str(e)}), 400

    # session.commit()
    return jsonify({'batchref', batchref}), 201


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}
