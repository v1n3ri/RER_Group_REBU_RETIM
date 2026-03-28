# Improved Debugging and Token Validation Logic

import jwt
from flask import request, jsonify
from functools import wraps

# Your secret key
SECRET_KEY = 'your_secret_key'

# Token validation decorator

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception as e:
            return jsonify({'message': f'Token is invalid! {str(e)}'}), 401

        return f(*args, **kwargs)

    return decorated

# Example of using the decorator
@token_required
def get_user_info():
    return jsonify({'message': 'This is protected data.'})

# Improved debugging information
if __name__ == '__main__':
    app.run(debug=True)