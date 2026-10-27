mport os, secrets, string, threading, time
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
 {"q":"¿Qué harías si te despertaras y fueras invisible durante una hora?","o":["Iría a un museo","Gastaría la hora haciendo bromas","Me quedaría en casa","Intentaría descubrir cómo pasó"],"a":3,"why":"¡Lo primero sería averiguar qué ha ocurrido!"},
 {"q":"¿Qué objeto sería más útil en una isla desierta?","o":["Una navaja multiusos","Un espejo de mano","Un altavoz","Un cojín"],"a":0,"why":"Una navaja multiusos puede servir para muchas tareas prácticas."},
 {"q":"¿Qué ingrediente no suele llevar una tortilla de patatas tradicional?","o":["Patata","Huevo","Cebolla opcional","Chocolate"],"a":3,"why":"El chocolate no es un ingrediente habitual de la tortilla de patatas."},
 {"q":"¿Cuál de estos animales es un mamífero?","o":["Tortuga","Delfín","Trucha","Gallina"],"a":1,"why":"El delfín respira aire y alimenta a sus crías con leche."},
 {"q":"¿Qué planeta es conocido como el planeta rojo?","o":["Venus","Marte","Júpiter","Mercurio"],"a":1,"why":"Marte tiene un aspecto rojizo por los minerales de hierro de su superficie."},
 {"q":"¿Cuántos lados tiene un hexágono?","o":["Cinco","Seis","Siete","Ocho"],"a":1,"why":"Un hexágono tiene seis lados."},
 {"q":"¿Qué instrumento tiene teclas blancas y negras?","o":["Piano","Violín","Trompeta","Batería"],"a":0,"why":"El piano tiene un teclado con teclas blancas y negras."},
 {"q":"¿Qué país tiene forma de bota en el mapa?","o":["Grecia","Italia","Portugal","Noruega"],"a":1,"why":"La península italiana recuerda a la forma de una bota."},
 {"q":"¿Qué bebida se prepara tradicionalmente con hojas de té?","o":["Limonada","Té","Horchata","Chocolate caliente"],"a":1,"why":"El té se prepara infusionando hojas de la planta del té."},
 {"q":"¿Qué deporte se juega en Wimbledon?","o":["Baloncesto","Tenis","Rugby","Béisbol"],"a":1,"why":"Wimbledon es uno de los torneos más famosos de tenis."},
 {"q":"¿Qué se necesita para hacer crecer una planta sana?","o":["Agua y luz adecuadas","Solo música","Pintura y papel","Hielo permanente"],"a":0,"why":"Las plantas necesitan agua, luz y otros recursos para crecer."},
 {"q":"¿Cuál de estos alimentos suele ser una legumbre?","o":["Lenteja","Manzana","Lechuga","Arroz"],"a":0,"why":"Las lentejas son legumbres ricas en proteínas y fibra."},
 {"q":"¿Qué continente es el más grande por superficie?","o":["Europa","África","Asia","Oceanía"],"a":2,"why":"Asia es el continente de mayor superficie."},
 {"q":"¿Qué aparato sirve para medir la temperatura?","o":["Barómetro","Termómetro","Cronómetro","Brújula"],"a":1,"why":"El termómetro mide la temperatura."},
 {"q":"¿Cuál es el resultado de 9 × 7?","o":["56","63","72","69"],"a":1,"why":"Nueve por siete es sesenta y tres."},
 {"q": "¿Qué planeta es conocido como el planeta rojo?", "o": ["Venus", "Marte", "Júpiter", "Mercurio"], "a": 1, "why": "Marte tiene un aspecto rojizo por los óxidos de hierro de su superficie."},
 {"q": "¿Cuántos lados tiene un hexágono?", "o": ["Cinco", "Seis", "Siete", "Ocho"], "a": 1, "why": "Un hexágono tiene seis lados."},
 {"q": "¿Cuál de estos animales es un mamífero que pone huevos?", "o": ["Delfín", "Murciélago", "Ornitorrinco", "Pingüino"], "a": 2, "why": "El ornitorrinco es un mamífero monotremo que pone huevos."},
 {"q": "¿En qué país está la ciudad de Kioto?", "o": ["China", "Japón", "Tailandia", "Corea del Sur"], "a": 1, "why": "Kioto es una ciudad histórica de Japón."},
 {"q": "¿Qué instrumento tiene teclas blancas y negras?", "o": ["Violín", "Flauta", "Piano", "Tambor"], "a": 2, "why": "El piano se toca mediante un teclado de teclas blancas y negras."},
 {"q": "¿Qué ingrediente es básico en un guacamole tradicional?", "o": ["Aguacate", "Calabacín", "Pepino", "Guisantes"], "a": 0, "why": "El aguacate es la base del guacamole."},
 {"q": "¿Cuántos minutos hay en dos horas y media?", "o": ["120", "130", "150", "180"], "a": 2, "why": "Dos horas son 120 minutos y media hora son 30: en total, 150."},
 {"q": "¿Qué gas absorben principalmente las plantas durante la fotosíntesis?", "o": ["Oxígeno", "Dióxido de carbono", "Helio", "Hidrógeno"], "a": 1, "why": "Las plantas utilizan dióxido de carbono, agua y luz para producir azúcares."},
 {"q": "¿Cuál es el océano más grande de la Tierra?", "o": ["Atlántico", "Índico", "Ártico", "Pacífico"], "a": 3, "why": "El océano Pacífico es el de mayor superficie."},
 {"q": "¿Qué deporte se juega en Wimbledon?", "o": ["Golf", "Tenis", "Críquet", "Baloncesto"], "a": 1, "why": "Wimbledon es uno de los torneos más conocidos de tenis."},
 {"q": "¿Qué figura geométrica tiene tres lados?", "o": ["Triángulo", "Cuadrado", "Pentágono", "Rombo"], "a": 0, "why": "Un triángulo tiene tres lados."},
 {"q": "¿Cuál de estos alimentos se elabora normalmente con cacao?", "o": ["Chocolate", "Hummus", "Pan de pita", "Gazpacho"], "a": 0, "why": "El cacao es uno de los ingredientes principales del chocolate."},
 {"q": "¿Qué órgano bombea la sangre por el cuerpo?", "o": ["Pulmón", "Hígado", "Corazón", "Riñón"], "a": 2, "why": "El corazón impulsa la sangre a través del sistema circulatorio."},
 {"q": "¿Cuál es la capital de Portugal?", "o": ["Oporto", "Lisboa", "Coímbra", "Faro"], "a": 1, "why": "Lisboa es la capital de Portugal."},
 {"q": "Si hoy es viernes, ¿qué día será dentro de tres días?", "o": ["Domingo", "Lunes", "Martes", "Miércoles"], "a": 1, "why": "Sábado es un día después, domingo dos y lunes tres."},
]
HOME = """
<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiz Party</title>
<style>
:root{color-scheme:dark;--ink:#1a1034;--purple:#30145c;--pink:#ff4f9a;--cyan:#45f2e0;--yellow:#ffe15a;--lav:#c7b4ff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 12% 12%,#6e31a5 0,transparent 30%),radial-gradient(circle at 88% 80%,#a51f75 0,transparent 27%),linear-gradient(135deg,#100923,#21103f 55%,#120b29);color:#fff;font-family:ui-rounded,"Trebuchet MS",system-ui,Arial;min-height:100vh;display:grid;place-items:center;padding:22px;overflow-x:hidden}
body:before{content:"✦　✧　✦　✧　✦";position:fixed;top:18px;left:4%;font-size:1.5rem;color:#ffe15a;opacity:.6;letter-spacing:12px;pointer-events:none}
.wrap{width:min(960px,100%);position:relative}h1{font-size:clamp(2.8rem,10vw,6rem);text-align:center;margin:0;line-height:1.05;letter-spacing:-3px;text-shadow:0 6px 0 #4b2478,0 12px 35px #0008}h1 span{color:var(--yellow)}.sub{text-align:center;color:#e1d7ff;margin:14px 0 32px;font-size:1.08rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px}.card,.panel{background:linear-gradient(145deg,#35215eeb,#21143feb);border:1px solid #a88be966;border-radius:26px;padding:26px;box-shadow:0 18px 45px #0005;backdrop-filter:blur(8px);transition:transform .2s,border-color .2s}.card:hover{transform:translateY(-5px);border-color:#ffe15a}.card h2{font-size:1.35rem}.btn{width:100%;border:0;border-radius:15px;padding:15px;font-weight:1000;font-size:1rem;background:linear-gradient(135deg,#ffe15a,#ffb84d);color:#25113e;cursor:pointer;box-shadow:0 5px 0 #b97825;transition:transform .15s,filter .15s}.btn:hover{filter:brightness(1.08);transform:translateY(-2px)}.btn:active{transform:translateY(2px);box-shadow:0 2px 0 #b97825}.cyan{background:linear-gradient(135deg,#67fff0,#40c9ff);box-shadow:0 5px 0 #218baf}.field{width:100%;padding:15px;border-radius:14px;border:1px solid #a58bd6;background:#140d2a;color:white;font-size:1rem;margin:10px 0 14px;outline:none}.field:focus{border-color:var(--cyan);box-shadow:0 0 0 3px #45f2e033}.muted{color:#d4c9ef}.err{color:#ff9cc5;min-height:1.4em}.creator{text-align:center;color:#d8d0f3;font-size:.95rem;margin:28px 0 4px}.creator strong{color:var(--yellow)}
@media(max-width:560px){body{padding:15px}body:before{font-size:1rem;letter-spacing:4px}h1{letter-spacing:-1px}.card,.panel{padding:20px;border-radius:20px}}
</style><main class="wrap"><h1>QUIZ <span>PARTY!</span> 🎉</h1><div class="sub">Junta a tu equipo. Responde rápido. ¡Que gane el mejor!</div><div class="cards"><section class="card"><h2>🎤 Presentar concurso</h2><p class="muted">Crea una sala y muestra el marcador en tu Mac.</p><button class="btn" onclick="createRoom()">Crear sala</button><div id="err" class="err"></div></section><section class="card"><h2>📱 Unirme a una partida</h2><p class="muted">Introduce el código de seis caracteres.</p><form onsubmit="join(event)"><input class="field" id="code" placeholder="CÓDIGO DE SALA" maxlength="6" required><button class="btn cyan">Entrar a jugar</button></form><div id="joinErr" class="err"></div></section></div><div class="creator">✨ Creado por <strong>julzzz.zzzz</strong> ✨</div></main>
<script>
async function createRoom(){let r=await fetch('/api/create',{method:'POST'}),d=await r.json();location.href='/host/'+d.code+'?key='+encodeURIComponent(d.key)}
async function join(e){e.preventDefault();let c=document.querySelector('#code').value.trim().toUpperCase(),r=await fetch('/api/check/'+c),d=await r.json();if(!r.ok){document.querySelector('#joinErr').textContent=d.error;return}location.href='/play/'+c}
document.querySelector('#code').addEventListener('input',e=>e.target.value=e.target.value.toUpperCase());
</script></main>"""
HOST = """
<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quiz Party TV</title>
<style>
:root{--ink:#1a1034;--pink:#ff4f9a;--cyan:#45f2e0;--yellow:#ffe15a;--lav:#bca5ff}
*{box-sizing:border-box}body{margin:0;padding:22px;background:radial-gradient(circle at 12% 8%,#6930a1,transparent 32%),radial-gradient(circle at 92% 90%,#a32674,transparent 30%),linear-gradient(135deg,#100923,#21103f 55%,#120b29);color:white;font-family:ui-rounded,"Trebuchet MS",system-ui,Arial;min-height:100vh}
.top{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;max-width:1400px;margin:auto}.logo{font-size:clamp(1.9rem,5vw,3.4rem);font-weight:1000;letter-spacing:-1px;text-shadow:0 5px 0 #4b2478}.logo span,.code,.score,.big{color:var(--yellow)}.pill,.box{background:linear-gradient(145deg,#35215eef,#21143feb);border:1px solid #a88be966;border-radius:24px;padding:22px;box-shadow:0 18px 45px #0004}.pill{font-weight:900}.layout{display:grid;grid-template-columns:2fr 1fr;gap:20px;margin:22px auto;max-width:1400px}.q{font-size:clamp(1.6rem,4vw,3rem);font-weight:1000;line-height:1.15;margin:18px 0}.answers{display:grid;grid-template-columns:1fr 1fr;gap:13px}.ans{padding:19px;border-radius:17px;color:#190e30;font-weight:1000;background:linear-gradient(135deg,#65fff0,#37d8cf);box-shadow:0 5px 0 #188d8d}.ans:nth-child(2){background:linear-gradient(135deg,#ff8ac0,#ff4f9a);box-shadow:0 5px 0 #b72568}.ans:nth-child(3){background:linear-gradient(135deg,#fff080,#ffd34d);box-shadow:0 5px 0 #bd8b1d}.ans:nth-child(4){background:linear-gradient(135deg,#d0bcff,#a98aff);box-shadow:0 5px 0 #6d4dc0}.btn{border:0;border-radius:14px;padding:14px 18px;font-weight:1000;background:linear-gradient(135deg,#ffe15a,#ffb84d);color:#25113e;cursor:pointer;margin:10px 8px 0 0;box-shadow:0 4px 0 #b97825}.btn:hover{filter:brightness(1.08);transform:translateY(-1px)}.btn:disabled{opacity:.45;cursor:not-allowed;transform:none}.team{display:flex;justify-content:space-between;gap:10px;border-bottom:1px solid #8069a6;padding:13px 0}.muted{color:#d4c9ef}.hidden{display:none}.big{font-size:clamp(2rem,7vw,4rem);font-weight:1000}.timer{display:inline-flex;align-items:center;gap:8px;margin:12px 0;padding:10px 20px;border-radius:16px;background:linear-gradient(135deg,#67fff0,#40c9ff);color:#190e30;font-size:2rem;font-weight:1000;box-shadow:0 5px 0 #218baf;min-width:130px;justify-content:center}.timer.urgent{background:linear-gradient(135deg,#ff8ac0,#ff4f9a);color:white;box-shadow:0 5px 0 #b72568;animation:pulse .65s infinite alternate}@keyframes pulse{to{transform:scale(1.04)}}#reveal{margin-top:16px;border-color:#ffe15a}#scores .team:first-child{color:#ffe15a}@media(max-width:750px){body{padding:14px}.layout{grid-template-columns:1fr}.answers{grid-template-columns:1fr}.box,.pill{padding:18px;border-radius:20px}.ans{padding:16px}.top{align-items:flex-start}}
</style><div class="top"><div class="logo">QUIZ <span>PARTY!</span> 🎉</div><div class="pill">CÓDIGO: <span class="code">{{code}}</span></div></div><div class="layout"><main class="box"><section id="lobby"><h2>🎤 ¡Que empiece la fiesta!</h2><p class="muted">Comparte la URL pública y el código. Tus amigos entran desde el móvil y escriben su nombre y equipo.</p><h2>Jugadores: <span id="count">0</span></h2><button class="btn" onclick="act('start')">🚀 Empezar partida</button></section><section id="game" class="hidden"><div class="muted" id="round"></div><div class="timer" id="timer">⏱️ 20 s</div><div class="q" id="question"></div><div class="answers" id="answers"></div><div class="box hidden" id="reveal"></div><button class="btn" id="revealBtn" onclick="act('reveal')">👀 Mostrar respuesta</button><button class="btn" id="nextBtn" onclick="act('next')">Siguiente pregunta ➜</button><p class="muted" id="answered"></p></section><section id="done" class="hidden"><div class="big">🏆 ¡Tenemos ganador!</div><h2 id="winner"></h2><p id="final" class="muted"></p><button class="btn" onclick="location.href='/'">Crear otra partida</button></section><p id="err" class="muted"></p></main><aside class="box"><h2>🏆 Marcador</h2><div id="scores" class="muted">Esperando equipos…</div><h2>👥 Jugadores</h2><div id="players" class="muted">Aún no se ha unido nadie.</div></aside></div>
<script>
const C={{code|tojson}},K=new URLSearchParams(location.search).get('key');function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function act(a){try{let r=await fetch('/api/'+C+'/'+a,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key:K})}),d=await r.json();if(!r.ok)throw Error(d.error);refresh()}catch(e){document.querySelector('#err').textContent=e.message}}
async function refresh(){try{let r=await fetch('/api/'+C+'/state?key='+encodeURIComponent(K)),s=await r.json();document.querySelector('#count').textContent=s.players.length;document.querySelector('#players').innerHTML=s.players.map(p=>'📱 '+esc(p.name)+' · '+esc(p.team)).join('<br>')||'Aún no se ha unido nadie.';document.querySelector('#scores').innerHTML=s.teams.map(t=>'<div class="team"><b>'+esc(t.name)+'</b><span class="score">'+t.score+'</span></div>').join('')||'Esperando equipos…';document.querySelector('#lobby').classList.toggle('hidden',s.status!=='lobby');document.querySelector('#game').classList.toggle('hidden',s.status!=='playing');document.querySelector('#done').classList.toggle('hidden',s.status!=='finished');
if(s.status==='playing'){let q=s.question;document.querySelector('#round').textContent='PREGUNTA '+q.number+' / '+q.total;let timer=document.querySelector('#timer');timer.textContent='⏱️ '+s.time_left+' s';timer.classList.toggle('urgent',s.time_left<=5);document.querySelector('#question').textContent=q.text;document.querySelector('#answers').innerHTML=q.options.map((o,i)=>'<div class="ans">'+String.fromCharCode(65+i)+'. '+esc(o)+'</div>').join('');document.querySelector('#reveal').classList.toggle('hidden',!s.revealed);document.querySelector('#reveal').innerHTML=s.revealed?'Respuesta correcta: <b>'+esc(q.options[q.correct])+'</b><br>'+esc(q.explanation):'';document.querySelector('#revealBtn').disabled=s.revealed;document.querySelector('#nextBtn').textContent=q.number===q.total?'🏁 Ver ganador':'Siguiente pregunta ➜';document.querySelector('#answered').textContent='Respuestas: '+s.answers+' / '+s.players.length}
if(s.status==='finished'){document.querySelector('#winner').textContent=s.winners.join(' & ')||'Sin equipos';document.querySelector('#final').textContent='Puntuación ganadora: '+s.winning_score+' puntos.'}}catch(e){document.querySelector('#err').textContent=e.message}}
refresh();setInterval(refresh,1500);
</script>"""
PLAYER = """
<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Jugar Quiz Party</title>
<style>
:root{--ink:#1a1034;--pink:#ff4f9a;--cyan:#45f2e0;--yellow:#ffe15a;--lav:#bca5ff}
*{box-sizing:border-box}body{margin:0;padding:18px;background:radial-gradient(circle at 10% 8%,#6930a1,transparent 32%),radial-gradient(circle at 92% 90%,#a32674,transparent 30%),linear-gradient(135deg,#100923,#21103f 55%,#120b29);color:white;font-family:ui-rounded,"Trebuchet MS",system-ui,Arial;display:flex;justify-content:center;min-height:100vh}.wrap{width:min(650px,100%)}h1{text-align:center;font-size:clamp(2.5rem,9vw,4rem);letter-spacing:-2px;text-shadow:0 5px 0 #4b2478;margin:12px 0 24px}h1 span{color:var(--yellow)}.box{background:linear-gradient(145deg,#35215eef,#21143feb);border:1px solid #a88be966;border-radius:25px;padding:24px;margin:16px 0;box-shadow:0 18px 45px #0004}.field{width:100%;padding:15px;border-radius:14px;border:1px solid #a58bd6;background:#140d2a;color:white;font-size:1rem;margin:8px 0 16px;outline:none}.field:focus{border-color:var(--cyan);box-shadow:0 0 0 3px #45f2e033}.btn,.choice{width:100%;border:0;border-radius:15px;padding:16px;font-size:1rem;font-weight:1000;background:linear-gradient(135deg,#ffe15a,#ffb84d);color:#25113e;cursor:pointer;box-shadow:0 5px 0 #b97825;transition:transform .15s,filter .15s}.btn:hover,.choice:hover{filter:brightness(1.08);transform:translateY(-2px)}.choice{text-align:left;background:linear-gradient(135deg,#65fff0,#37d8cf);margin:7px 0;box-shadow:0 4px 0 #188d8d}.choice:nth-child(2){background:linear-gradient(135deg,#ff8ac0,#ff4f9a);box-shadow:0 4px 0 #b72568}.choice:nth-child(3){background:linear-gradient(135deg,#fff080,#ffd34d);box-shadow:0 4px 0 #bd8b1d}.choice:nth-child(4){background:linear-gradient(135deg,#d0bcff,#a98aff);box-shadow:0 4px 0 #6d4dc0}.choice:disabled{opacity:.6;cursor:not-allowed;transform:none}.q{font-size:clamp(1.4rem,5vw,1.9rem);font-weight:1000;line-height:1.2;margin:15px 0}.muted{color:#d4c9ef}.hidden{display:none}.status{background:#332354;border:1px solid #8069a6;border-radius:15px;padding:14px;margin:12px 0}.err{color:#ff9cc5}.timer{display:inline-flex;align-items:center;justify-content:center;margin:10px 0;padding:10px 18px;border-radius:14px;background:linear-gradient(135deg,#67fff0,#40c9ff);color:#190e30;font-size:1.7rem;font-weight:1000;box-shadow:0 4px 0 #218baf;min-width:125px}.timer.urgent{background:linear-gradient(135deg,#ff8ac0,#ff4f9a);color:white;box-shadow:0 4px 0 #b72568;animation:pulse .65s infinite alternate}@keyframes pulse{to{transform:scale(1.04)}}@media(max-width:480px){body{padding:10px}.box{padding:19px;border-radius:20px}}
</style><main class="wrap"><h1>QUIZ <span>PARTY!</span> 🎉</h1><section class="box" id="join"><div class="muted">SALA {{code}}</div><h2>¡Únete al concurso!</h2><p class="muted">Para compartir equipo, escribid exactamente el mismo nombre.</p><form id="form"><label>Tu nombre</label><input class="field" id="name" maxlength="24" required placeholder="Ej. Julia"><label>Nombre del equipo</label><input class="field" id="team" maxlength="24" required placeholder="Ej. Los Tornados"><button class="btn">Entrar a jugar 📱</button></form><div id="err" class="err"></div></section><section class="box hidden" id="play"><div id="who" class="muted"></div><div id="status" class="status">Esperando al anfitrión…</div><div id="area" class="hidden"><div id="round" class="muted"></div><div id="timer" class="timer">⏱️ 20 s</div><div id="question" class="q"></div><div id="choices"></div><div id="feedback" class="status hidden"></div></div><div id="done" class="hidden"><h2 id="winner"></h2><p id="final" class="muted"></p></div></section></main>
<script>
const C={{code|tojson}};let pid=localStorage.getItem('qp_'+C),joined=false,last=-1,answered=false;function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
document.querySelector('#form').addEventListener('submit',async e=>{e.preventDefault();try{let r=await fetch('/api/'+C+'/join',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.querySelector('#name').value.trim(),team:document.querySelector('#team').value.trim(),player_id:pid})}),d=await r.json();if(!r.ok)throw Error(d.error);pid=d.player_id;localStorage.setItem('qp_'+C,pid);joined=true;document.querySelector('#join').classList.add('hidden');document.querySelector('#play').classList.remove('hidden');document.querySelector('#who').textContent=d.name+' · '+d.team;poll()}catch(x){document.querySelector('#err').textContent=x.message}});
async function answer(i){if(answered)return;let r=await fetch('/api/'+C+'/answer',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({player_id:pid,choice:i})}),d=await r.json();if(!r.ok){document.querySelector('#status').textContent=d.error;return}answered=true;document.querySelectorAll('.choice').forEach(b=>b.disabled=true);document.querySelector('#feedback').classList.remove('hidden');document.querySelector('#feedback').textContent=d.correct?'🎉 ¡Correcto! +100 puntos para tu equipo.':'¡Respuesta enviada! Espera la solución.'}
async function poll(){if(!joined)return;try{let r=await fetch('/api/'+C+'/state?player_id='+encodeURIComponent(pid)),s=await r.json(),area=document.querySelector('#area');if(s.status==='lobby'){document.querySelector('#status').textContent='¡Estás dentro! Espera a que empiece.';area.classList.add('hidden')}
if(s.status==='playing'){document.querySelector('#status').textContent=s.revealed?'Respuesta revelada en la pantalla principal.':'¡Elige tu respuesta!';area.classList.remove('hidden');let q=s.question;document.querySelector('#round').textContent='PREGUNTA '+q.number+' / '+q.total;let timer=document.querySelector('#timer');timer.textContent='⏱️ '+s.time_left+' s';timer.classList.toggle('urgent',s.time_left<=5);document.querySelector('#question').textContent=q.text;if(last!==q.number){last=q.number;answered=false;document.querySelector('#feedback').classList.add('hidden');document.querySelector('#choices').innerHTML=q.options.map((o,i)=>'<button class="choice" onclick="answer('+i+')">'+String.fromCharCode(65+i)+'. '+esc(o)+'</button>').join('')}if(answered||s.revealed)document.querySelectorAll('.choice').forEach(b=>b.disabled=true);if(s.revealed){document.querySelector('#feedback').classList.remove('hidden');document.querySelector('#feedback').textContent='Respuesta: '+q.options[q.correct]+'. '+q.explanation;document.querySelectorAll('.choice').forEach(b=>b.disabled=true)}}
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
    ts=scores(r);ps=[{"id":p["id"],"name":p["name"],"team":p["team"]} for p in r["players"].values()];q=None;count=0;time_left=20
    if r["status"]=="playing":
        elapsed=time.time()-(r.get("question_started_at") or time.time())
        time_left=max(0,20-int(elapsed))
        if time_left<=0:
            r["revealed"]=True
        item=r["qs"][r["i"]];count=len(r["answers"].get(str(r["i"]),{}));q={"number":r["i"]+1,"total":len(r["qs"]),"text":item["q"],"options":item["o"]}
        if r["revealed"]:q.update(correct=item["a"],explanation=item["why"])
    winners=[];winning=0
    if r["status"]=="finished" and ts:
        winning=max(t["score"] for t in ts);winners=[t["name"] for t in ts if t["score"]==winning]
    return {"status":r["status"],"teams":ts,"players":ps,"question":q,"revealed":r["revealed"],"answers":count,"time_left":time_left,"winners":winners,"winning_score":winning}
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
        c,k=new_code(),secrets.token_urlsafe(24);rooms[c]={"code":c,"key":k,"status":"lobby","teams":{},"players":{},"i":-1,"revealed":False,"answers":{},"qs":questions.copy(),"question_started_at":None}
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
            r["status"]="playing";r["i"]=0;r["revealed"]=False;r["question_started_at"]=time.time()
        elif action=="reveal":
            if r["status"]!="playing":return jsonify(error="No hay pregunta activa."),400
            r["revealed"]=True
        elif action=="next":
            if not r["revealed"]:return jsonify(error="Primero muestra la respuesta."),400
            if r["i"]+1>=len(r["qs"]):r["status"]="finished"
            else:r["i"]+=1;r["revealed"]=False;r["question_started_at"]=time.time()
        else:return jsonify(error="Acción desconocida."),404
        return jsonify(ok=True)
@app.post("/api/<code>/answer")
def submit(code):
    with lock:
        r=room(code)
        if not r:return jsonify(error="Sala no encontrada."),404
        if r["status"]!="playing" or r["revealed"]:return jsonify(error="La pregunta está cerrada."),400
        if time.time()-(r.get("question_started_at") or time.time())>=20:
            r["revealed"]=True
            return jsonify(error="¡Se acabó el tiempo!"),400
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
