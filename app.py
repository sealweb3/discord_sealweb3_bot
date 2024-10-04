import os
import json
from dotenv import load_dotenv
from flask import Flask, jsonify

load_dotenv()

app = Flask(__name__)

SECRET_KEY = os.getenv('SECRET_KEY')
MAIN_DIR = os.getenv('MAIN_DIR')

@app.route('/users/<string:token>', methods=['GET'])
def get_data(token):

    if token == SECRET_KEY:
        try:
            with open(f'{MAIN_DIR}/users.json') as f:
                data = json.load(f)
            return jsonify(data)
        except FileNotFoundError:
            return jsonify({"error": "Data file not found"}), 404
        except Exception as e:
            return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    else:
        jsonify({"error": f"Bad token: {token}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
