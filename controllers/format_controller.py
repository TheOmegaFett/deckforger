from flask import Blueprint, jsonify, request
from models.format import Format
from init import db

format_blueprint = Blueprint('format', __name__)

@format_blueprint.route('/formats', methods=['GET'])
def get_formats():
    formats = Format.query.all()
    return jsonify([format.to_dict() for format in formats])

@format_blueprint.route('/formats/<int:format_id>', methods=['GET'])
def get_format(format_id):
    format = Format.query.get_or_404(format_id)
    return jsonify(format.to_dict())

@format_blueprint.route('/formats', methods=['POST'])
def create_format():
    data = request.get_json()
    
    # Validation
    required_fields = ['name', 'description']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
        
    # Check for duplicate format names
    if Format.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Format name already exists'}), 409

    new_format = Format(
        name=data['name'],
        description=data['description']
    )
    
    db.session.add(new_format)
    db.session.commit()
    
    return jsonify(new_format.to_dict()), 201

@format_blueprint.route('/formats/<int:format_id>', methods=['PUT'])
def update_format(format_id):
    format = Format.query.get_or_404(format_id)
    data = request.get_json()
    
    if 'name' in data:
        existing_format = Format.query.filter_by(name=data['name']).first()
        if existing_format and existing_format.id != format_id:
            return jsonify({'error': 'Format name already exists'}), 409
    
    # Update fields
    for field in ['name', 'description']:
        if field in data:
            setattr(format, field, data[field])
    
    db.session.commit()
    return jsonify(format.to_dict())

@format_blueprint.route('/formats/<int:format_id>', methods=['DELETE'])
def delete_format(format_id):
    format = Format.query.get_or_404(format_id)
    db.session.delete(format)
    db.session.commit()
    return jsonify({'message': 'Format deleted successfully'}), 200
