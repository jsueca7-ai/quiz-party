# Quiz Party

## Ejecutar en macOS
En Terminal:

```bash
cd ~/QuizParty
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Abre http://127.0.0.1:5000 en el Mac. Detén con Control+C.

## Publicar online con Render
1. Crea un repositorio de GitHub y sube `app.py`, `requirements.txt`, `Procfile` y `render.yaml`.
2. En Render, conecta GitHub y crea un Web Service desde ese repositorio.
3. Confirma el despliegue usando los valores de `render.yaml`.
4. Abre la URL pública de Render en el Mac, pulsa Crear sala y comparte esa URL y el código con tus amigos.
5. En los móviles, abre la URL, introduce el código, el nombre y el equipo. Para jugar juntos deben escribir exactamente el mismo nombre de equipo.

## Reglas
Una respuesta correcta suma 100 puntos al equipo. El anfitrión inicia, revela cada respuesta y avanza a la siguiente. Al final aparece el equipo ganador.

## Limitaciones
Las partidas se guardan en memoria. Si el servicio se reinicia o se duerme, se pierde la sala. Mantén una sola instancia. Prototipo para amigos; no tiene protección avanzada contra trampas.
