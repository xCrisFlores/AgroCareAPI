from Controllers.user_controller import user_bp
from Controllers.autoencoder_controller import create_ae_blueprint

def register_routes(app, autoencoder, ae_trained_flag):
    # Blueprint de usuarios
    app.register_blueprint(user_bp, url_prefix='/api')

    # Crear y registrar el blueprint del AutoEncoder dinámicamente
    ae_bp = create_ae_blueprint(autoencoder, ae_trained_flag)
    app.register_blueprint(ae_bp, url_prefix='/api')
