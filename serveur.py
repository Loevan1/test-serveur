# serveur.py
import asyncio
import websockets
import json
import os

SCORES_FILE = "scores.json"

# Charger les scores depuis le fichier
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
    classement = sorted(scores, key=lambda x: x["score"], reverse=True)
    return classement

async def handler(websocket):
    
    print("il y a une connexion")
    
    async for message in websocket:
        
        data = json.loads(message)
        pseudo = data.get("pseudo")
        score = data.get("score")
        print(f"{pseudo} a {score} points")
        enregistrer_score(pseudo, score)
        classement = get_classement()
        classement_str = ""
        top_10 = classement[:10]
        for i, joueur in enumerate(top_10, start=1):
            ligne = f"{i}.  {joueur['pseudo']} - {joueur['score']} points"
            classement_str += ligne + "\n"

        await websocket.send(classement_str.strip()) 
        
        
    
            
    

async def main():
    port = int(os.environ.get("PORT", 8765)) 
    print("🔄 Lancement du serveur WebSocket...")
    async with websockets.serve(handler, port, 8765):
        print("✅ Serveur WebSocket en ligne sur ws://localhost:8765")
        print(websockets.__version__)
        await asyncio.Future()  # Boucle infinie

if __name__ == "__main__":
    asyncio.run(main())
