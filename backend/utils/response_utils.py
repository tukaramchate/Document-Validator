from flask import jsonify


def success_response(data=None, message=None, status_code=200):
    """Create a standardized success response."""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status_code


def error_response(message, error_code='ERROR', status_code=400):
    """Create a standardized error response."""
    return jsonify({
        'success': False,
        'error': {
            'code': error_code,
            'message': message
        }
    }), status_code


def paginated_response(items, total, page, per_page, item_name='items'):
    """Create a standardized paginated response."""
    per_page = max(per_page, 1)  # Guard against ZeroDivisionError
    return jsonify({
        'success': True,
        'data': {
            item_name: items,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        }
    }), 200
