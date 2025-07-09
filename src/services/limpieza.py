# webscraping/limpieza.py
import pandas as pd
import re
import unicodedata
import os
from langdetect import detect, DetectorFactory
from langdetect.lang_detect_exception import LangDetectException
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
DetectorFactory.seed = 0

class LimpiezaComentarios:
    def __init__(self, archivo_csv="comentarios_tiktok.csv"):
        self.archivo_csv = archivo_csv
        if not os.path.exists(archivo_csv):
            raise FileNotFoundError(f"No se encontró el archivo {archivo_csv}")
        self.df = pd.read_csv(archivo_csv)
        self.stopwords_es = set(stopwords.words("spanish"))

    def limpiar_texto(self, texto, eliminar_numeros=True, quitar_stopwords=False):
        if pd.isna(texto):
            return ""
        texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8", "ignore")
        texto = texto.lower()
        texto = re.sub(r"http\S+|www\S+|https\S+", "", texto)
        texto = re.sub(r"@\w+|#\w+", "", texto)
        texto = re.sub(r"[^\w\s]", "", texto)
        if eliminar_numeros:
            texto = re.sub(r"\d+", "", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        if quitar_stopwords:
            texto = " ".join([p for p in texto.split() if p not in self.stopwords_es])
        return texto

    def es_espanol(self, texto):
        try:
            return detect(texto) == "es"
        except LangDetectException:
            return False

    def procesar(self, salida_csv="comentarios_tiktok_limpio.csv"):
        self.df["usuario_limpio"] = self.df["usuario"].apply(lambda x: self.limpiar_texto(x, eliminar_numeros=False))
        self.df["comentario_limpio"] = self.df["comentario"].apply(
            lambda x: self.limpiar_texto(x, eliminar_numeros=True, quitar_stopwords=True)
        )
        self.df = self.df.drop_duplicates(subset=["comentario_limpio"])
        self.df = self.df[self.df["comentario_limpio"].str.split().str.len() >= 3]

        self.df["es_espanol"] = self.df["comentario_limpio"].apply(self.es_espanol)
        self.df = self.df[self.df["es_espanol"]]
        self.df = self.df.drop(columns=["es_espanol"])
        
        self.df = self.df[["usuario_limpio", "comentario_limpio"]]
        self.df.columns = ["usuario", "comentario"]
        
        self.df.to_csv(salida_csv, index=False, encoding="utf-8")
        print(f"Limpieza y guardado completado en {salida_csv}")
