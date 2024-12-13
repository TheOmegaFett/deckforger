from datetime import datetime
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError, validates
from init import db
from models.cardset import CardSet
from schemas.cardset_schema import set_schema, sets_schema

cardset_controller = Blueprint("set_controller", __name__)

# Create a new Set
@cardset_controller.route("/sets", methods=["POST"])
def create_set():
    data = request.json
    new_set = CardSet(
        name=data["name"],
        release_date=data.get("release_date"),
        description=data.get("description")
    )
    db.session.add(new_set)
    db.session.commit()
    return set_schema.jsonify(new_set), 201

@validates('name')
def validate_name(self, value):
    if len(value) < 1:
        raise ValidationError('Set name must not be empty')
    if len(value) > 100:
        raise ValidationError('Set name must be less than 100 characters')

@validates('release_date')
def validate_release_date(self, value):
    if value > datetime.now():
        raise ValidationError('Release date cannot be in the future')

# Read all Sets
@cardset_controller.route("/sets", methods=["GET"])
def get_sets():
    sets = CardSet.query.all()
    return sets_schema.jsonify(sets)

# Read one Set
@cardset_controller.route("/sets/<int:set_id>", methods=["GET"])
def get_set(set_id):
    set_ = CardSet.query.get(set_id)
    if not set_:
        return jsonify({"error": "Set not found"}), 404
    return set_schema.jsonify(set_)

# Update a Set
@cardset_controller.route("/sets/<int:set_id>", methods=["PUT"])
def update_set(set_id):
    set_ = CardSet.query.get(set_id)
    if not set_:
        return jsonify({"error": "Set not found"}), 404

    data = request.json
    set_.name = data.get("name", set_.name)
    set_.release_date = data.get("release_date", set_.release_date)
    set_.description = data.get("description", set_.description)
    db.session.commit()
    return set_schema.jsonify(set_)

# Delete a Set
@cardset_controller.route("/sets/<int:set_id>", methods=["DELETE"])
def delete_set(set_id):
    set_ = CardSet.query.get(set_id)
    if not set_:
        return jsonify({"error": "Set not found"}), 404

    db.session.delete(set_)
    db.session.commit()
    return jsonify({"message": "Set deleted successfully!"})
