# JWT 認証 (token_requiredデコレータ):

# token_required 関数は、他のエンドポイントにアクセスする前に JWT トークンがクライアントの Cookie に含まれているかどうかを確認します。
# トークンがない場合や無効な場合は、401 エラーを返します。
# トークンが有効な場合、デコードして current_user_id を取得し、ラップされた関数に渡します。
# /productsエンドポイント:

# 認証が必要で、認証に成功すると、外部 API (https://dummyjson.com/products) から製品情報を取得します。
# 取得した製品情報を整理して、JSON 形式でクライアントに返します。
# /authエンドポイント:

# ユーザー名とパスワードを POST リクエストで受け取り、users.json からユーザー情報を読み込んで認証を行います。
# 認証が成功すると、JWT トークンを発行し、クライアントに Cookie として返します。





import requests 
from flask import Flask, jsonify, request, make_response
import jwt
from functools import wraps
import json
import os
from jwt.exceptions import DecodeError


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) #秘密鍵生成
port = int(os.environ.get('PORT', 5000))

@app.route("/")
def home():
    return "Hello, this is a Flask Microservice"


# ------APIエンドポイントの定義------


#'/'にアクセスするときの認証のための関数
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get('token')
        if not token:
            return jsonify({'error': 'Authorization token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user_id = data['user_id']
        except DecodeError:
            return jsonify({'error': 'Authorization token is invalid'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated



BASE_URL = "https://dummyjson.com"

@app.route('/products', methods=['GET'])
@token_required
def get_products(current_user_id):
    headers = {'Authorization': f'Bearer {request.cookies.get("token")}'}
    response = requests.get(f"{BASE_URL}/products", headers=headers)
    if response.status_code != 200:
        return jsonify({'error': response.json().get('message', 'An error occurred')}), response.status_code
    products = []
    for product in response.json().get('products', []):
        product_data = {
            'id': product.get('id'),
            'title': product.get('title'),
            'brand': product.get('brand', 'Unknown'),  # デフォルト値を設定
            'price': product.get('price'),
            'description': product.get('description')
        }
        products.append(product_data)
    return jsonify({'data': products}), 200 if products else 204



with open('/var/www/micro_app/users.json', 'r') as f:
    users = json.load(f)
@app.route('/auth', methods=['POST'])
def authenticate_user():
    if request.headers['Content-Type'] != 'application/json':
        return jsonify({'error': 'Unsupported Media Type'}), 415
    username = request.json.get('username')
    password = request.json.get('password')
    for user in users:
        if user['username'] == username and user['password'] == password:
            token = jwt.encode({'user_id': user['id']}, app.config['SECRET_KEY'],algorithm="HS256")
            response = make_response(jsonify({'message': 'Authentication successful'}))
            response.set_cookie('token', token)
            return response, 200
    return jsonify({'error': 'Invalid username or password'}), 401



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=port)