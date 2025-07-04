import re
from flask import request, jsonify, Blueprint
from .extensions import db
from .models import User 
from .exceptions import InvalidAPIUsage

utils_bp = Blueprint('utils', __name__, url_prefix='/api/utils')

@utils_bp.route('/')
def utils_root():
    return jsonify({"status": "utils_works"}), 200

def validate_request(req, validation_rules):
    """Валидация входящих данных"""
    if not req.is_json:
        raise InvalidAPIUsage("Request must be JSON", 400)
    
    data = req.get_json()
    errors = {}
    
    for field, rules in validation_rules.items():
        # Проверка обязательных полей
        if rules.get('required') and field not in data:
            errors[field] = "This field is required"
            continue
            
        value = data.get(field)
        
        # Проверка типа
        if 'type' in rules and value is not None:
            if rules['type'] == 'string' and not isinstance(value, str):
                errors[field] = "Must be a string"
            elif rules['type'] == 'integer' and not isinstance(value, int):
                errors[field] = "Must be an integer"
        
        # Проверка минимальной длины
        if 'minlength' in rules and value is not None:
            if len(str(value)) < rules['minlength']:
                errors[field] = f"Must be at least {rules['minlength']} characters"
        
        # Проверка по регулярному выражению
        if 'regex' in rules and value is not None:
            if rules['regex'] == 'email' and not re.match(r'[^@]+@[^@]+\.[^@]+', value):
                errors[field] = "Invalid email format"
    
    if errors:
        raise InvalidAPIUsage("Validation failed", 400, {'errors': errors})
    
    return data
    
@utils_bp.route('/test-db')
def test_db():
    try:
        db.session.execute('SELECT 1').scalar()
        return {"status": "Database OK"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
        
def validate_request(data, required_fields):
    """Отдельная функция, не привязанная к Blueprint"""
    for field in required_fields:
        if field not in data:
            return False
    return True
