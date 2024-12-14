from init import db

class FormatRestriction(db.Model):
    __tablename__ = 'format_restrictions'
    
    id = db.Column(db.Integer, primary_key=True)
    format_id = db.Column(db.Integer, db.ForeignKey('formats.id'), nullable=False)
    set_id = db.Column(db.Integer, db.ForeignKey('sets.id'), nullable=False)
    valid_from = db.Column(db.Date, nullable=False)
    valid_until = db.Column(db.Date)
    
    format = db.relationship('Format', back_populates='restrictions')
    card_set = db.relationship('CardSet', back_populates='format_restrictions')
