#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify, abort
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

# GET all bakeries
@app.route('/bakeries')
def bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(bakeries, 200)

# GET a specific bakery
@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH'])
def bakery_by_id(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        abort(404, description="Bakery not found.")

    if request.method == 'GET':
        return make_response(bakery.to_dict(), 200)

    # PATCH bakery name
    elif request.method == 'PATCH':
        data = request.form
        if 'name' in data:
            bakery.name = data['name']
            db.session.commit()
        return make_response(bakery.to_dict(), 200)

# GET all baked goods ordered by price (descending)
@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_by_price_serialized = [bg.to_dict() for bg in baked_goods_by_price]
    return make_response(baked_goods_by_price_serialized, 200)

# GET the most expensive baked good
@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not most_expensive:
        abort(404, description="No baked goods found.")
    return make_response(most_expensive.to_dict(), 200)

# POST a new baked good
@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form
    try:
        new_bg = BakedGood(
            name=data['name'],
            price=float(data['price']),
            bakery_id=int(data['bakery_id'])
        )
        db.session.add(new_bg)
        db.session.commit()
        return make_response(new_bg.to_dict(), 201)
    except Exception as e:
        return make_response({"error": str(e)}, 400)

# DELETE a baked good by ID
@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)
    if not baked_good:
        abort(404, description="Baked good not found.")

    db.session.delete(baked_good)
    db.session.commit()
    return make_response({"message": "Baked good deleted successfully."}, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
