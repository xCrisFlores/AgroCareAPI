from quart import Blueprint, request, jsonify
from Middleware.jwt_middleware import require_auth
import asyncio
from supabase import create_client
import os

from Models import AutoEncoder

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

def create_ae_blueprint(autoencoder: AutoEncoder, ae_trained_flag):
    ae_bp = Blueprint('ae_bp', __name__) 

    @ae_bp.route('/recomendaciones', methods=['POST'])
    @require_auth()
    async def get_recomendaciones():
        if not ae_trained_flag[0]:
            return jsonify({"error": "AutoEncoder todavía se está entrenando, intenta más tarde"}), 503

        data = await request.get_json()
        total_cultivos = data.get("total_cultivos")
        temperatura = data.get("temperatura")
        humedad = data.get("humedad")
        precipitacion = data.get("precipitacion")

        if total_cultivos is None or temperatura is None or humedad is None or precipitacion is None:
            return jsonify({"error": "Datos invalidos o insuficientes"}), 400
        if total_cultivos > 22:
            return jsonify({"error": "El máximo de cultivos a recomendar es de 22"}), 400

        sample = [temperatura, precipitacion, humedad]
        top_cultivos = autoencoder.get_recomendations([sample], top_n=total_cultivos)
        keys_only = [autoencoder.clases_esp.get(c["key"], c["key"]) for c in top_cultivos]

       
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: supabase.table("cultivos")
                            .select("*")
                            .in_("key_cultivo", keys_only)
                            .execute()
        )

       
        data_map = {c["key_cultivo"]: c for c in response.data}

        cultivos_ordered = []
        for rank, c in enumerate(top_cultivos, start=1):
            db_item = data_map.get(autoencoder.clases_esp.get(c["key"], c["key"]), {})
            nombre = str(db_item.get("nombre") or "")
            cuidados = str(db_item.get("cuidados") or "")
            merma = str(db_item.get("merma") or "")
            descripcion = str(db_item.get("descripcion") or "")
            crecimiento = str(db_item.get("crecimiento") or "")

            item = {
                "nombre": nombre,
                "rank": rank,
                "cuidados": cuidados,
                "merma": merma,
                "descripcion": descripcion,
                "crecimiento": crecimiento
            }
            cultivos_ordered.append(item)

        return jsonify({"cultivos": cultivos_ordered}), 200

    return ae_bp
