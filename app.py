from quart import Quart
from quart_cors import cors
from Routes.routes import register_routes
from Models.AutoEncoder import AutoEncoder
import asyncio
from dotenv import load_dotenv

load_dotenv()
app = Quart(__name__)
app = cors(app, allow_origin="*")

autoencoder = AutoEncoder()
ae_trained_flag = [False]

register_routes(app, autoencoder, ae_trained_flag)

@app.before_serving
async def startup():
    print("Entrenando AutoEncoder...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, autoencoder.train, 50)
    ae_trained_flag[0] = True
    print("AutoEncoder entrenado")

@app.route("/")
async def root():
    return {"status": "Servidor corriendo", "ae_trained": ae_trained_flag[0]}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
