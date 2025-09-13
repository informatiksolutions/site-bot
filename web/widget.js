(function(){
  const api = (window.SITEBOT_API || "http://localhost:8000");
  const bubble = document.createElement('div');
  bubble.id = 'sitebot-bubble';
  bubble.innerText = 'Fragen?';
  document.body.appendChild(bubble);

  const panel = document.createElement('div');
  panel.id = 'sitebot-panel';
  panel.innerHTML = `
    <div class="sb-header">Wie kann ich helfen?</div>
    <div class="sb-suggestions">
      <button data-q="Preise">Preise</button>
      <button data-q="Kontakt">Kontakt</button>
      <button data-q="IT Support">IT Support</button>
      <button data-q="Backup">Backup</button>
    </div>
    <div class="sb-messages"></div>
    <div class="sb-input">
      <input placeholder="Frage eingeben…" />
      <button>Senden</button>
    </div>`;
  document.body.appendChild(panel);

  function toggle(){ panel.classList.toggle('open'); }
  bubble.onclick = toggle;

  panel.querySelectorAll('.sb-suggestions button').forEach(b=>{
    b.onclick = ()=> send(b.dataset.q);
  });
  panel.querySelector('.sb-input button').onclick = ()=>{
    const v = panel.querySelector('input').value.trim();
    if(v) send(v);
  };

  async function send(q){
    addMsg('user', q);
    const r = await fetch(api + '/query', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q})});
    const data = await r.json();
    if(data.answer){ addMsg('bot', data.answer); }
    (data.cards||[]).forEach(c=> addCard(c));
  }

  function addMsg(role, text){
    const m = document.createElement('div');
    m.className = 'sb-msg ' + role;
    m.textContent = text;
    panel.querySelector('.sb-messages').appendChild(m);
  }
  function addCard(c){
    const el = document.createElement('a');
    el.className = 'sb-card';
    el.href = c.url; el.target = '_blank';
    el.innerHTML = `<div class="t">${c.title}</div><div class="s">${c.snippet||''}</div><div class="cta">${c.cta||'Ansehen'}</div>`;
    panel.querySelector('.sb-messages').appendChild(el);
  }
})();
