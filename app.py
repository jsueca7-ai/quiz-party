import os, secrets, string, threading
from flask import Flask, jsonify, request, render_template_string
app = Flask(__name__)
rooms = {}
lock = threading.Lock()
questions = [
 {"q":"¿Qué excusa suena más sospechosa para llegar tarde?","o":["Me secuestró una cabra","El ascensor estaba de vacaciones","Mi GPS me mandó a Portugal","Todas podrían ser verdad"],"a":3,"why":"¡Cualquiera sería una excusa memorable!"},
 {"q":"¿Qué llevaría un pingüino a su boda?","o":["Traje de gala","Pista de hielo","Pescado para el menú","Todo lo anterior"],"a":3,"why":"¡Una boda de pingüinos tendría todo eso!"},
 {"q":"¿Qué mensaje sería peor mandar al grupo del trabajo por error?","o":["¡Buen finde!","¿Quién se comió mi yogur?","Un audio de 7 minutos roncando","Un pulgar arriba"],"a":2,"why":"Un audio largo de ronquidos sería bastante incómodo."},
 {"q":"¿Quién sorprendería más en una competición de baile animal?","o":["Un flamenco","Un canguro","Una serpiente","Un perezoso"],"a":0,"why":"¡El flamenco tiene nombre de baile!"},
 {"q":"¿Qué sería más raro encontrar en una nevera?","o":["Leche","Un imán","Un zapato limpio","Un táper"],"a":2,"why":"Los zapatos no suelen guardarse en la nevera."},
 {"q":"Tu amigo dice «una canción más» en el karaoke. ¿Qué significa?","o":["Que se va ya","Que quedan tres horas","Que perdió la voz","Que quiere pagar"],"a":1,"why":"Esa canción más suele convertirse en muchas canciones."},
 {"q":"¿Qué superpoder sería más útil en una fiesta?","o":["Encontrar el baño","Recargar las patatas fritas","Saber quién puso esa canción","Todos son imprescindibles"],"a":3,"why":"Los tres poderes serían muy útiles."},
 {"q":"¿Qué animal sería el peor compañero de piso?","o":["Un mapache que roba cosas","Una tortuga tranquila","Un pez que no habla","Una mariposa"],"a":0,"why":"Un mapache podría robar comida y revolver la casa."},
 {"q":"¿Qué frase anuncia que la noche se va a alargar?","o":["Mañana madrugo","Me pongo el pijama","¿Quién pide comida?","Ya he pedido el taxi"],"a":2,"why":"Pedir comida suele indicar que la reunión continúa."},
 {"q":"¿Cuál sería el peor nombre para un restaurante elegante?","o":["La Trufa Dorada","Mantel y Romero","El Tupper Sudado","Azafrán"],"a":2,"why":"«El Tupper Sudado» no suena muy apetecible."},
 {"q":"¿Qué talento inútil impresionaría más en una fiesta?","o":["Imitar una impresora","Decir los meses al revés","Hacer beatbox con la axila","Cualquiera de ellos"],"a":3,"why":"Cualquiera de esos talentos absurdos podría impresionar."},
 {"q":"¿Qué suele desaparecer en una casa compartida?","o":["El cargador","La última croqueta","La tapa del táper","Todo lo anterior"],"a":3,"why":"Los tres objetos suelen desaparecer misteriosamente."},
 {"q":"¿Qué haría un vampiro si olvidara su capa?","o":["Pedir una sábana","Cancelar la noche","Ponerse una toalla","Dramatizarlo todo"],"a":3,"why":"Olvidar la capa sería motivo de mucho drama."},
 {"q":"¿Cuál es el peor sitio para que suene tu alarma?","o":["En el sofá de casa","En una biblioteca","En una fiesta ruidosa","En el coche con música"],"a":1,"why":"Una biblioteca suele ser un lugar silencioso."},
 {"q":"¿Qué desaparece de la mesa primero en una fiesta?","o":["Las patatas","El último trozo de pizza","Los vasos limpios","Depende de los invitados"],"a":3,"why":"¡Depende del grupo y de lo que más les guste!"},
]
HOME = """
<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiz Party</title>
<style>.creator{text-align:center;color:#d8d0f3;font-size:.95rem;margin:24px 0 4px}.creator strong{color:#ffd34d}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#46227c,#100a27 70%);color:white;font-family:system-ui,Arial;min-height:100vh;display:grid;place-items:center;padding:20px}.wrap{width:min(900px,100%)}h1{font-size:clamp(2.5rem,9vw,5rem);text-align:center;margin:0}h1 span{color:#ffd34d}.sub{text-align:center;color:#d8d0f3;margin:10px 0 28px}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:18px}.card,.panel{background:#211744;border:1px solid #59458a;border-radius:22px;padding:24px}.btn{width:100%;border:0;border-radius:12px;padding:14px;font-weight:900;font-size:1rem;background:#ffd34d;color:#190e30;cursor:pointer}.cyan{background:#37e5e5}.field{width:100%;padding:14px;border-radius:12px;border:1px solid #69569a;background:#120d27;color:white;font-size:1rem;margin:10px 0 14px}.muted{color:#c7bddf}.err{color:#ff9cc5;min-height:1.4em}
</style><main class="wrap"><h1>QUIZ <span>PARTY!</span> 🎉</h1><div class="sub">Junta a tu equipo. Responde rápido. ¡Que gane el mejor!</div><div class="cards"><section class="card"><h2>🎤 Presentar concurso</h2><p class="muted">Crea una sala y muestra el marcador en tu Mac.</p><button class="btn" onclick="createRoom()">Crear sala</button><div id="err" class="err"></div></section><section class="card"><h2>📱 Unirme a una partida</h2><p class="muted">Introduce el código de seis caracteres.</p><form onsubmit="join(event)"><input class="field" id="code" placeholder="CÓDIGO DE SALA" maxlength="6" required><button class="btn cyan">Entrar a jugar</button></form><div id="joinErr" class="err"></div></section></div><div class="creator">✨ Creado por <strong>julzzz.zzzz</strong> ✨</div></main>
<script>
async function createRoom(){let r=await fetch('/api/create',{method:'POST'}),d=await r.json();location.href='/host/'+d.code+'?key='+encodeURIComponent(d.key)}
async function join(e){e.preventDefault();let c=document.querySelector('#code').value.trim().toUpperCase(),r=await fetch('/api/check/'+c),d=await r.json();if(!r.ok){document.querySelector('#joinErr').textContent=d.error;return}location.href='/play/'+c}
document.querySelector('#code').addEventListener('input',e=>e.target.value=e.target.value.toUpperCase());
</script></main>"""
HOST = """
<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiz Party TV</title>
<style>
*{box-sizing:border-box}body{margin:0;padding:20px;background:radial-gradient(circle at top,#46227c,#100a27 70%);color:white;font-family:system-ui,Arial}.top{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}.logo{font-size:clamp(1.8rem,5vw,3rem);font-weight:1000}.logo span,.code,.score,.big{color:#ffd34d}.pill,.box{background:#211744;border:1px solid #59458a;border-radius:20px;padding:20px}.layout{display:grid;grid-template-columns:2fr 1fr;gap:18px;margin:20px auto;max-width:1400px}.q{font-size:clamp(1.5rem,4vw,2.8rem);font-weight:900}.answers{display:grid;grid-template-columns:1fr 1fr;gap:12px}.ans{padding:18px;border-radius:14px;color:#190e30;font-weight:900;background:#37e5e5}.ans:nth-child(2){background:#ff4f9a}.ans:nth-child(3){background:#ffd34d}.ans:nth-child(4){background:#b8a0ff}.btn{border:0;border-radius:12px;padding:14px;font-weight:900;background:#ffd34d;color:#190e30;cursor:pointer;margin:10px 8px 0 0}.team{display:flex;justify-content:space-between;border-bottom:1px solid #59458a;padding:12px 0}.muted{color:#c7bddf}.hidden{display:none}.big{font-size:clamp(2rem,7vw,4rem)}@media(max-width:750px){.layout{grid-template-columns:1fr}.answers{grid-template-columns:1fr}}
</style><div class="top"><div class="logo">QUIZ <span>PARTY!</span> 🎉</div><div class="pill">CÓDIGO: <span class="code">{{code}}</span></div></div><div class="layout"><main class="box"><section id="lobby"><h2>🎤 ¡Que empiece la fiesta!</h2><p class="muted">Comparte la URL pública y el código. Tus amigos entran desde el móvil y escriben su nombre y equipo.</p><h2>Jugadores: <span id="count">0</span></h2><button class="btn" onclick="act('start')">🚀 Empezar partida</button></section><section id="game" class="hidden"><div class="muted" id="round"></div><div class="q" id="question"></div><div class="answers" id="answers"></div><div class="box hidden" id="reveal"></div><button class="btn" id="revealBtn" onclick="act('reveal')">👀 Mostrar respuesta</button><button class="btn" id="nextBtn" onclick="act('next')">Siguiente pregunta ➜</button><p class="muted" id="answered"></p></section><section id="done" class="hidden"><div class="big">🏆 ¡Tenemos ganador!</div><h2 id="winner"></h2><p id="final" class="muted"></p><button class="btn" onclick="location.href='/'">Crear otra partida</button></section><p id="err" class="muted"></p></main><aside class="box"><h2>🏆 Marcador</h2><div id="scores" class="muted">Esperando equipos…</div><h2>👥 Jugadores</h2><div id="players" class="muted">Aún no se ha unido nadie.</div></aside></div>
<script>
const C={{code|tojson}},K=new URLSearchParams(location.search).get('key');function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function act(a){try{let r=await fetch('/api/'+C+'/'+a,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:K})}),d=await r.json();if(!r.ok)throw Error(d.error);refresh()}catch(e){document.querySelector('#err').textContent=e.message}}
async function refresh(){try{let r=await fetch('/api/'+C+'/state?key='+encodeURIComponent(K)),s=await r.json();document.querySelector('#count').textContent=s.players.length;document.querySelector('#players').innerHTML=s.players.map(p=>'📱 '+esc(p.name)+' · '+esc(p.team)).join('<br>')||'Aún no se ha unido nadie.';document.querySelector('#scores').innerHTML=s.teams.map(t=>'<div class="team"><b>'+esc(t.name)+'</b><span class="score">'+t.score+'</span></div>').join('')||'Esperando equipos…';document.querySelector('#lobby').classList.toggle('hidden',s.status!=='lobby');document.querySelector('#game').classList.toggle('hidden',s.status!=='playing');document.querySelector('#done').classList.toggle('hidden',s.status!=='finished');
if(s.status==='playing'){let q=s.question;document.querySelector('#round').textContent='PREGUNTA '+q.number+' / '+q.total;document.querySelector('#question').textContent=q.text;document.querySelector('#answers').innerHTML=q.options.map((o,i)=>'<div class="ans">'+String.fromCharCode(65+i)+'. '+esc(o)+'</div>').join('');document.querySelector('#reveal').classList.toggle('hidden',!s.revealed);document.querySelector('#reveal').innerHTML=s.revealed?'Respuesta correcta: <b>'+esc(q.options[q.correct])+'</b><br>'+esc(q.explanation):'';document.querySelector('#revealBtn').disabled=s.revealed;document.querySelector('#nextBtn').textContent=q.number===q.total?'🏁 Ver ganador':'Siguiente pregunta ➜';document.querySelector('#answered').textContent='Respuestas: '+s.answers+' / '+s.players.length}
if(s.status==='finished'){document.querySelector('#winner').textContent=s.winners.join(' & ')||'Sin equipos';document.querySelector('#final').textContent='Puntuación ganadora: '+s.winning_score+' puntos.'}}catch(e){document.querySelector('#err').textContent=e.message}}
refresh();setInterval(refresh,1500);
</script>"""
PLAYER = """
<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Jugar Quiz Party</title>
<style>
*{box-sizing:border-box}body{margin:0;padding:16px;background:radial-gradient(circle at top,#46227c,#100a27 70%);color:white;font-family:system-ui,Arial;display:flex;justify-content:center}.wrap{width:min(650px,100%)}h1{text-align:center}h1 span{color:#ffd34d}.box{background:#211744;border:1px solid #59458a;border-radius:20px;padding:22px;margin:16px 0}.field{width:100%;padding:14px;border-radius:12px;border:1px solid #69569a;background:#120d27;color:white;font-size:1rem;margin:8px 0 14px}.btn,.choice{width:100%;border:0;border-radius:12px;padding:15px;font-size:1rem;font-weight:900;background:#ffd34d;color:#190e30;cursor:pointer}.choice{text-align:left;background:#37e5e5;margin:5px 0}.choice:nth-child(2){background:#ff4f9a}.choice:nth-child(3){background:#ffd34d}.choice:nth-child(4){background:#b8a0ff}.q{font-size:1.5rem;font-weight:900}.muted{color:#c7bddf}.hidden{display:none}.status{background:#33265b;border-radius:12px;padding:12px;margin:12px 0}.err{color:#ff9cc5}
</style><main class="wrap"><h1>QUIZ <span>PARTY!</span> 🎉</h1><section class="box" id="join"><div class="muted">SALA {{code}}</div><h2>¡Únete al concurso!</h2><p class="muted">Para compartir equipo, escribid exactamente el mismo nombre.</p><form id="form"><label>Tu nombre</label><input class="field" id="name" maxlength="24" required placeholder="Ej. Julia"><label>Nombre del equipo</label><input class="field" id="team" maxlength="24" required placeholder="Ej. Los Tornados"><button class="btn">Entrar a jugar 📱</button></form><div id="err" class="err"></div></section><section class="box hidden" id="play"><div id="who" class="muted"></div><div id="status" class="status">Esperando al anfitrión…</div><div id="area" class="hidden"><div id="round" class="muted"></div><div id="question" class="q"></div><div id="choices"></div><div id="feedback" class="status hidden"></div></div><div id="done" class="hidden"><h2 id="winner"></h2><p id="final" class="muted"></p></div></section></main>
<script>
const C={{code|tojson}};let pid=localStorage.getItem('qp_'+C),joined=false,last=-1,answered=false;function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
document.querySelector('#form').addEventListener('submit',async e=>{e.preventDefault();try{let r=await fetch('/api/'+C+'/join',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.querySelector('#name').value.trim(),team:document.querySelector('#team').value.trim(),player_id:pid})}),d=await r.json();if(!r.ok)throw Error(d.error);pid=d.player_id;localStorage.setItem('qp_'+C,pid);joined=true;document.querySelector('#join').classList.add('hidden');document.querySelector('#play').classList.remove('hidden');document.querySelector('#who').textContent=d.name+' · '+d.team;poll()}catch(x){document.querySelector('#err').textContent=x.message}});
async function answer(i){if(answered)return;let r=await fetch('/api/'+C+'/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({player_id:pid,choice:i})}),d=await r.json();if(!r.ok){document.querySelector('#status').textContent=d.error;return}answered=true;document.querySelectorAll('.choice').forEach(b=>b.disabled=true);document.querySelector('#feedback').classList.remove('hidden');document.querySelector('#feedback').textContent=d.correct?'🎉 ¡Correcto! +100 puntos para tu equipo.':'¡Respuesta enviada! Espera la solución.'}
async function poll(){if(!joined)return;try{let r=await fetch('/api/'+C+'/state?player_id='+encodeURIComponent(pid)),s=await r.json(),area=document.querySelector('#area');if(s.status==='lobby'){document.querySelector('#status').textContent='¡Estás dentro! Espera a que empiece.';area.classList.add('hidden')}
if(s.status==='playing'){document.querySelector('#status').textContent=s.revealed?'Respuesta revelada en la pantalla principal.':'¡Elige tu respuesta!';area.classList.remove('hidden');let q=s.question;document.querySelector('#round').textContent='PREGUNTA '+q.number+' / '+q.total;document.querySelector('#question').textContent=q.text;if(last!==q.number){last=q.number;answered=false;document.querySelector('#feedback').classList.add('hidden');document.querySelector('#choices').innerHTML=q.options.map((o,i)=>'<button class="choice" onclick="answer('+i+')">'+String.fromCharCode(65+i)+'. '+esc(o)+'</button>').join('')}if(answered||s.revealed)document.querySelectorAll('.choice').forEach(b=>b.disabled=true);if(s.revealed){document.querySelector('#feedback').classList.remove('hidden');document.querySelector('#feedback').textContent='Respuesta: '+q.options[q.correct]+'. '+q.explanation;document.querySelectorAll('.choice').forEach(b=>b.disabled=true)}}
if(s.status==='finished'){area.classList.add('hidden');document.querySelector('#status').textContent='¡Fin de la partida!';document.querySelector('#done').classList.remove('hidden');document.querySelector('#winner').textContent='🏆 Ganador: '+s.winners.join(' & ');document.querySelector('#final').textContent='Puntuación: '+s.winning_score+' puntos.'}}catch(e){document.querySelector('#status').textContent='Reconectando…'}setTimeout(poll,1500)}
</script>"""
def new_code():
    chars=string.ascii_uppercase+string.digits
    while True:
        c="".join(secrets.choice(chars) for _ in range(6))
        if c not in rooms:return c
def room(code):return rooms.get((code or "").upper())
def scores(r):return sorted([{"name":n,"score":v["score"]} for n,v in r["teams"].items()],key=lambda x:(-x["score"],x["name"].lower()))
def state(r):
    ts=scores(r);ps=[{"id":p["id"],"name":p["name"],"team":p["team"]} for p in r["players"].values()];q=None;count=0
    if r["status"]=="playing":
        item=r["qs"][r["i"]];count=len(r["answers"].get(str(r["i"]),{}));q={"number":r["i"]+1,"total":len(r["qs"]),"text":item["q"],"options":item["o"]}
        if r["revealed"]:q.update(correct=item["a"],explanation=item["why"])
    winners=[];winning=0
    if r["status"]=="finished" and ts:
        winning=max(t["score"] for t in ts);winners=[t["name"] for t in ts if t["score"]==winning]
    return {"status":r["status"],"teams":ts,"players":ps,"question":q,"revealed":r["revealed"],"answers":count,"winners":winners,"winning_score":winning}
@app.get("/")
def home():return render_template_string(HOME)
@app.get("/host/<code>")
def host(code):
    if not room(code):return "Sala no encontrada",404
    return render_template_string(HOST,code=code.upper())
@app.get("/play/<code>")
def player(code):
    if not room(code):return "Sala no encontrada",404
    return render_template_string(PLAYER,code=code.upper())
@app.post("/api/create")
def create():
    with lock:
        c,k=new_code(),secrets.token_urlsafe(24);rooms[c]={"code":c,"key":k,"status":"lobby","teams":{},"players":{},"i":-1,"revealed":False,"answers":{},"qs":questions.copy()}
    return jsonify(code=c,key=k)
@app.get("/api/check/<code>")
def check(code):
    if not room(code):return jsonify(error="No existe esa sala."),404
    return jsonify(ok=True)
@app.post("/api/<code>/join")
def join(code):
    with lock:
        r=room(code)
        if not r:return jsonify(error="Sala no encontrada."),404
        if r["status"]!="lobby":return jsonify(error="La partida ya ha empezado."),400
        d=request.get_json(silent=True) or {};name=str(d.get("name","")).strip()[:24];team=str(d.get("team","")).strip()[:24]
        if not name or not team:return jsonify(error="Escribe nombre y equipo."),400
        pid=str(d.get("player_id") or "")
        if pid not in r["players"]:pid=secrets.token_urlsafe(12)
        r["players"][pid]={"id":pid,"name":name,"team":team}
        if team not in r["teams"]:r["teams"][team]={"score":0}
        return jsonify(player_id=pid,name=name,team=team)
@app.get("/api/<code>/state")
def get_state(code):
    r=room(code)
    if not r:return jsonify(error="Sala no encontrada."),404
    return jsonify(state(r))
@app.post("/api/<code>/<action>")
def host_action(code,action):
    with lock:
        r=room(code);d=request.get_json(silent=True) or {}
        if not r:return jsonify(error="Sala no encontrada."),404
        if not d.get("key") or not secrets.compare_digest(r["key"],str(d["key"])):return jsonify(error="Solo el anfitrión puede hacer esto."),403
        if action=="start":
            if not r["players"]:return jsonify(error="Primero debe entrar alguien desde un móvil."),400
            r["status"]="playing";r["i"]=0;r["revealed"]=False
        elif action=="reveal":
            if r["status"]!="playing":return jsonify(error="No hay pregunta activa."),400
            r["revealed"]=True
        elif action=="next":
            if not r["revealed"]:return jsonify(error="Primero muestra la respuesta."),400
            if r["i"]+1>=len(r["qs"]):r["status"]="finished"
            else:r["i"]+=1;r["revealed"]=False
        else:return jsonify(error="Acción desconocida."),404
        return jsonify(ok=True)
@app.post("/api/<code>/answer")
def submit(code):
    with lock:
        r=room(code)
        if not r:return jsonify(error="Sala no encontrada."),404
        if r["status"]!="playing" or r["revealed"]:return jsonify(error="La pregunta está cerrada."),400
        d=request.get_json(silent=True) or {};pid=str(d.get("player_id",""));p=r["players"].get(pid)
        if not p:return jsonify(error="Vuelve a entrar en la sala."),403
        try:a=int(d.get("choice"))
        except (TypeError,ValueError):return jsonify(error="Respuesta inválida."),400
        i=r["i"];q=r["qs"][i];key=str(i);r["answers"].setdefault(key,{})
        if pid in r["answers"][key]:return jsonify(error="Ya has respondido."),400
        if a<0 or a>3:return jsonify(error="Respuesta inválida."),400
        ok=a==q["a"];r["answers"][key][pid]=a
        if ok:r["teams"][p["team"]]["score"]+=100
        return jsonify(correct=ok,points=100 if ok else 0)
@app.get("/health")
def health():return jsonify(status="ok")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
