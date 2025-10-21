import bcrypt
from quart import Blueprint, request, jsonify
from supabase import create_client
import os
import asyncio
from dotenv import load_dotenv
from Middleware.jwt_factory import create_jwt
from Middleware.jwt_middleware import require_auth


load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

user_bp = Blueprint('user_bp', __name__) 

@user_bp.route('/login', methods=['POST'])
async def login():
    try:
        data = await request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: supabase.table("usuarios")
                    .select("*")
                    .or_(f"email.eq.{email},username.eq.{email}")
                    .execute()
        )

        if not response.data or len(response.data) == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404

        user = response.data[0]

        if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            return jsonify({"error": "Contraseña incorrecta"}), 401

        token = create_jwt({
            "user_id": str(user["id"]),
        }, expire_in_sec=3600)

        return jsonify({
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@user_bp.route('/usuarios/<int:id>', methods=['PUT'])
@require_auth()
async def update_user(id):
    try:
        data = await request.get_json()
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: supabase.table("usuarios").update(data).eq("id", id).execute()
        )
        if response.count == 0:
            return jsonify({"error": "Usuario no encontrado"}), 404
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route('/register', methods=['POST'])
async def create():
    try:
        data = await request.get_json()
        password = data.get("password")
        if not password:
            return jsonify({"error": "Password requerida"}), 400

        # Generar hash seguro
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        data["password"] = hashed.decode('utf-8') 

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: supabase.table("usuarios").insert(data).execute()
        )
        return jsonify(response.data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
