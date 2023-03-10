from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ
from marshmallow import post_load, fields, ValidationError
load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models
class Toy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float)
    inventory_quantity = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.name} {self.description} {self.price} {self.inventory_quantity}'

# Schemas
class ToySchema(ma.Schema):
    id = fields.Integer(primary_key=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    price = fields.Float()
    inventory_quantity = fields.Integer()
    class Meta:
        fields = ("id", "name", "description", "price", "inventory_quantity")

    @post_load
    def create_toy(self, data, **kwargs):
        return Toy(**data)
    
toy_schema = ToySchema()
toys_schema = ToySchema(many=True)

# Resources
class ToyListResource(Resource):
    def get(self):
        all_toys = Toy.query.all()
        return toys_schema.dump(all_toys)
    
    def post(self):
        form_data = request.get_json()
        try:
            new_toy = toy_schema.load(form_data)
            db.session.add(new_toy)
            db.session.commit()
            return toy_schema.dump(new_toy), 201
        except ValidationError as err:
            return err.messages, 400
        
class ToyResource(Resource):
    def get(self, toy_id):
        toy_from_db = Toy.query.get_or_404(toy_id)
        return toy_schema.dump(toy_from_db)
    
    def delete(self, toy_id):
        toy_from_db = Toy.query.get_or_404(toy_id)
        db.session.delete(toy_from_db)
        return '', 204
    
    def put(self, toy_id):
        toy_from_db = Toy.query.get_or_404(toy_id)
        if 'name' in request.json:
            toy_from_db.name=request.json['name']
        if 'description' in request.json:
            toy_from_db.description=request.json['description']
        if 'price' in request.json:
            toy_from_db.price=request.json['price']
        if 'inventory_quantity' in request.json:
            toy_from_db.inventory_quantity=request.json['inventory_quantity']
        db.session.commit()
        return toy_schema.dump(toy_from_db)


# Routes
api.add_resource(ToyListResource, '/api/products/')
api.add_resource(ToyResource, '/api/products/<int:pk>')