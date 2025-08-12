# serveur.py
import os
import json
import asyncio
from aiohttp import web

SCORES_FILE = "scores.json"

# Gestion des scores
def charger_scores():
    if os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    return []

def enregistrer_score(pseudo, score):
    scores = charger_scores()
    for joueur in scores:
        if joueur["pseudo"] == pseudo:
            if score > joueur["score"]:
                joueur["score"] = score
            break
    else:
        scores.append({"pseudo": pseudo, "score": score})
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent=2)

def get_classement():
    scores = charger_scores()
    return sorted(scores, key=lambda x: x["score"], reverse=True)

# Handler WebSocket
async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    print("✅ Connexion WebSocket ouverte")

    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)
            pseudo = data.get("pseudo")
            score = data.get("score")
            print(f"{pseudo} a {score} points")

            enregistrer_score(pseudo, score)
            classement = get_classement()

            top_10 = classement[:10]
            classement_str = "\n".join(
                f"{i+1}. {j['pseudo']} - {j['score']} points"
                for i, j in enumerate(top_10)
            )
            await ws.send_str(classement_str.strip())

        elif msg.type == web.WSMsgType.ERROR:
            print(f"⚠ Erreur WS: {ws.exception()}")

    print("❌ Connexion WebSocket fermée")
    return ws

# Route HTTP pour test
async def index(request):
    return web.Response(text="Serveur WebSocket en ligne", content_type="text/plain")

# Création app aiohttp
app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/ws", websocket_handler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    web.run_app(app, host="0.0.0.0", port=port)

