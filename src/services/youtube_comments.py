import os
import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from langdetect import detect, DetectorFactory



# Establece semilla para resultados reproducibles en langdetect
DetectorFactory.seed = 0

# Carga la clave de YouTube desde .env (YT_API_KEY)
load_dotenv()
YT_API_KEY = os.getenv("YT_API_KEY")
youtube = build("youtube", "v3", developerKey=YT_API_KEY)

# Busca IDs de videos con relevancia en español
def search_videos(query, max_results=50):
    response = youtube.search().list(
        part="id",
        q=query,
        type="video",
        maxResults=max_results,
        relevanceLanguage="es"
    ).execute()
    return [item['id']['videoId'] for item in response.get('items', [])]

# Obtiene el texto de comentarios de un video, omitiendo videos con comentarios deshabilitados
def fetch_comment_texts(video_id):
    texts = []
    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )
    while request:
        try:
            response = request.execute()
        except HttpError as e:
            if e.resp.status == 403 and 'commentsDisabled' in str(e):
                print(f"Comentarios deshabilitados para video {video_id}, omitiendo...")
                return texts
            raise
        for item in response.get("items", []):
            text = item['snippet']['topLevelComment']['snippet'].get('textDisplay', '').strip()
            if text:
                texts.append(text)
        request = youtube.commentThreads().list_next(request, response)
    return texts

# Punto de entrada: busca temas, filtra español y guarda en CSV
def main():
    queries = [
        "Copa Mundial de Clubes FIFA 2025 ESpañol",
        "Fluminense vs Chelsea FC (0-2) | Resumen | Highlights Mundial de Clubes FIFA 2025™",
        "Palmeiras vs Chelsea FC (1-2) | Resumen | Highlights Mundial de Clubes FIFA 2025™",
        "SILVERSTONE NO DEFRAUDÓ: LLUVIA, CHOQUES, TRIUNFO DE NORRIS E HISTÓRICO PODIO DE HULKENBERG |RESUMEN",
        "NORRIS GANÓ CARRERA de LOCURA en GRAN BRETAÑA. PIASTRI, SEGUNDO. VERSTAPPEN, QUINTO | Formula 1",
        "Las fortalezas y debilidades de cada coche de F1 en 2025",
        "¡¡HULKENBERG PODIO!! ESCANDALO FIA? VERSTAPPEN la PIFIA - RESUMEN GP de GRAN BRETAÑA F1 2025",
        "La percepción incorrecta sobre Red Bull que explica sus primeros problemas en la F1 2025",
        "Todos los EQUIPOS de la F1 (para TONTOS)"
    ]
    all_texts = []
    for q in queries:
        video_ids = search_videos(q)
        for vid in video_ids:
            all_texts.extend(fetch_comment_texts(vid))

    # Filtra solo comentarios en español
    spanish_comments = []
    for text in all_texts:
        try:
            if detect(text) == 'es':
                spanish_comments.append(text)
        except:
            # Ignora textos muy cortos o detección fallida
            continue

    # Exporta a CSV
    df = pd.DataFrame({'comment': spanish_comments})
    df.to_csv("youtube_comments_sp.csv", index=False, encoding="utf-8-sig")
    print(f"Guardados {len(df)} comentarios en español en youtube_comments_sp.csv")

if __name__ == "__main__":
    main()
