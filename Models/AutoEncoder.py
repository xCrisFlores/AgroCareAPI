import pandas as pd
import numpy as np
from keras._tf_keras.keras.layers import Dense, Dropout, Input
from keras._tf_keras.keras.activations import relu
from keras._tf_keras.keras.optimizers import Adam
from keras._tf_keras.keras.losses import Huber
from keras._tf_keras.keras.models import Model

class AutoEncoder:
    def __init__(self):
        self.dataset, self.labels = self.prepare_dataset()
        self.clases_esp = {
            'rice': 'arroz',
            'maize': 'maiz',
            'chickpea': 'garbanzo',
            'kidneybeans': 'frijol_rojo',
            'pigeonpeas': 'guandu',
            'mothbeans': 'frijol_polilla',
            'mungbean': 'frijol_mungo',
            'blackgram': 'frijol_negro',
            'lentil': 'lenteja',
            'pomegranate': 'granada',
            'banana': 'platano',
            'mango': 'mango',
            'grapes': 'uva',
            'watermelon': 'sandia',
            'muskmelon': 'melon',
            'apple': 'manzana',
            'orange': 'naranja',
            'papaya': 'papaya',
            'coconut': 'coco',
            'cotton': 'algodon',
            'jute': 'yute',
            'coffee': 'cafe'
        }
        self.model = self.generate_model(input_dim=self.dataset.shape[1])
        self.class_profiles = None  

    def prepare_dataset(self):
        dataset = pd.read_csv('Crop_recommendation.csv')
        df = dataset[['temperature', 'rainfall', 'humidity']]
        df = (df - df.min()) / (df.max() - df.min())
        labels = dataset['label']
        return df, labels

    def generate_model(self, input_dim=3):
        inputs = Input(shape=(input_dim,))
        x = Dense(2, activation=relu)(inputs)
        x = Dropout(0.5)(x)
        latent = Dense(1, activation=relu)(x)
        x = Dense(2, activation=relu)(latent)
        x = Dropout(0.5)(x)
        outputs = Dense(input_dim, activation='sigmoid')(x)

        model = Model(inputs=inputs, outputs=outputs)
        model.compile(optimizer=Adam(learning_rate=0.001), loss=Huber(delta=0.1))
        return model

    def train(self, epochs=100, batch_size=64, val_split=0.2):
        print("DEBUG: Entrenando modelo...")
        X_train = np.array(self.dataset)
        self.model.fit(
            X_train, X_train,
            epochs=epochs,
            batch_size=batch_size,
            shuffle=True,
            validation_split=val_split,
            verbose=0
        )
        self.compute_class_profiles()
        print("DEBUG: Entrenamiento completado")

    def compute_class_profiles(self):
        self.class_profiles = {}
        for label in self.labels.unique():
            X_class = np.array(self.dataset[self.labels == label])
            reconstructed = self.model.predict(X_class, verbose=0)
            mean_pattern = reconstructed.mean(axis=0)
            self.class_profiles[label] = mean_pattern

    def predict_label(self, sample):
        if self.class_profiles is None:
            raise ValueError("Debes entrenar el modelo antes")
        sample = np.array(sample)
        reconstructed = self.model.predict(sample, verbose=0)
        errors = {}
        for label, mean_pattern in self.class_profiles.items():
            error = np.mean((reconstructed - mean_pattern) ** 2)
            errors[label] = error
        best_label = min(errors, key=errors.get)
        return best_label, errors
    
    def get_recomendations(self, sample, top_n=5):
        _, errors = self.predict_label(sample)
        sorted_crops = sorted(errors.items(), key=lambda x: x[1])[:top_n]
        result = []
        for key, err in sorted_crops:
            nombre_es = self.clases_esp.get(key, key)
            result.append({
                "key": key,
                "nombre": nombre_es,
                "error": err
            })
        return result