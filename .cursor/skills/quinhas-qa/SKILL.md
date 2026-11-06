---
name: quinhas-qa
description: QA, testes e prevenção de bugs para o Quinhas Ball Fighters. Use depois de qualquer mudança no jogo, ao caçar bug, ao verificar layout no desktop e no celular, ao testar teclado, controle e toque, ao medir combate, ou ao rodar a rodada Bugbot. Contém receitas de teste que funcionam no navegador do Cursor.
---

# QA — Quinhas Ball Fighters

Não há suíte automatizada. A garantia é **rodar o jogo e olhar**. "Li o código e parece certo" não é teste. Checklist completo em [checklist.md](checklist.md).

## Ciclo mínimo (toda mudança)

1. **Sintaxe**, da raiz do projeto:
   ```
   python .cursor/skills/quinhas-qa/scripts/check_syntax.py
   ```
2. **Servir** por HTTP (`file://` quebra imagem): `python -m http.server 8765` em segundo plano. Confirme que responde antes de abrir.
3. **Abrir no browser** (`browser_navigate`), esperar o boot (receita 1) e percorrer o fluxo que a mudança alcança.
4. **Conferir estado** por `Runtime.evaluate`, não só pela imagem.
5. **Console sem erro** (receita 7).
6. **Resoluções**: desktop largo, desktop baixo, celular em pé e deitado.
7. **Regressão**: refaça o fluxo vizinho (o outro modo, a tela de antes, o outro dispositivo). Checklist por área em `checklist.md`.
8. Corrija o que achou e repita os passos afetados. Pare o servidor ao terminar (se o ambiente permitir).

Sem browser disponível: diga isso no resumo final. Não declare "testado".

## Receitas (testadas)

Use `browser_cdp` → `Runtime.evaluate` com `returnByValue: true`. As variáveis do jogo (`st`, `scr`, `CH`, `ATK`, `fighters`…) são acessíveis porque o script é global.

**1. Esperar o boot e ler o estado**
```js
new Promise(r=>{let n=0;const iv=setInterval(()=>{n++;let ok=false;try{ok=!!(CH&&CH.q)}catch(e){}
 if(ok||n>100){clearInterval(iv);r(JSON.stringify({loaded:ok,scr:scr(),st,IS_TOUCH,DIFF}))}},100)})
```
Use `awaitPromise: true`. Se `loaded:false`, o boot quebrou: veja o console (TDZ ou sintaxe).

**2. Começar uma luta Versus sem clicar** (pula a seleção; testa só a luta)
```js
(async()=>{document.getElementById('title').style.display='none';
 await begin('ai','q','e',0);await new Promise(r=>setTimeout(r,2500));
 return JSON.stringify({st,hp:[p1.hp,p2.hp],x:[p1.x|0,p2.x|0]})})()
```

**3. Começar uma Arena e medir knockback**
```js
(async()=>{document.getElementById('title').style.display='none';
 await beginArena([{t:'human',dev:'k1',cid:'q',slot:0},{t:'ai',cid:'e',slot:1}]);
 await new Promise(r=>setTimeout(r,3500));const out=[];
 for(const hp of [100,70,40,15]){const v=fighters[1];v.hp=hp;v.x=400;v.kx=0;v.vy=0;v.on=true;v.inv=0;v.rsp=0;v.ko=false;
  v.hurt(fighters[0],ATK.k);out.push({hp,kx:+v.kx.toFixed(2),vy:+v.vy.toFixed(2)})}
 return JSON.stringify({st,ast,hits:out})})()
```
Lembre: `hurt` desconta o dano antes de calcular (`hp` efetivo = valor − `a.d`).

**4. Controle sem hardware** (stub de `navigator.getGamepads`)
```js
const btn=p=>({pressed:p,value:p?1:0});
const mk=down=>({connected:true,id:'Xbox 360 Controller (STANDARD GAMEPAD)',index:0,axes:[0,0,0,0],
  buttons:Array.from({length:17},(_,i)=>btn(down.includes(i)))});
const real=navigator.getGamepads; navigator.getGamepads=()=>[mk([2])];   // 2 = soco
gin(navigator.getGamepads()[0]).p   // true
navigator.getGamepads=real;
```
Para testar menu, deixe o stub ligado alguns quadros com o botão (0 confirmar, 1 voltar, 12–15 D-pad) e desligue. Para pad PlayStation, mude o `id` para conter `DualShock` ou `DualSense`. Para dois pads, devolva dois objetos na lista. **Zere o stub** ao terminar (recarregue a página).

**5. Celular**
- `?touch=1` na URL força `IS_TOUCH` (lobby de celular, controle virtual, sem prévia de corpo).
- Emulação (`Emulation.setDeviceMetricsOverride`) não muda a altura do `#stage`: **meça a altura real** (`getBoundingClientRect` do `#stage`) e, se preciso, defina a altura do estágio. Limpe com `Emulation.clearDeviceMetricsOverride` ao terminar.
- Teste em pé (~390×844) e deitado (~844×390), e uma tela baixa (altura < 420).

**6. Medir layout sem confiar no olho**
```js
const R=id=>{const e=document.getElementById(id);const b=e.getBoundingClientRect();return {x:b.x|0,y:b.y|0,w:b.width|0,h:b.height|0}};
// sobreposição: compare R('prompts') com R('back') / R('a4act'); corte: bottom > innerHeight; scroll: scrollHeight > innerHeight
```

**7. Console sem erro.** Antes de carregar a página, instale um coletor; depois de percorrer o fluxo, leia:
```js
// 1) logo depois de navegar (a página já carregou: rode e teste dali em diante)
window.__err=[];addEventListener('error',e=>__err.push(String(e.message)+' @'+(e.filename||'').split('/').pop()+':'+e.lineno));
addEventListener('unhandledrejection',e=>__err.push('promise: '+String(e.reason)));
// 2) depois do fluxo
JSON.stringify({errors:window.__err, badAssets:(typeof LOAD!=='undefined'&&LOAD.bad)||[]})
```
Erro que acontece no boot não passa por esse coletor: nesse caso `CH.q` não existir (receita 1) já acusa. Para o boot, use também `browser_cdp` com `Log.enable` / `Runtime.enable` antes de navegar, ou leia o console da aba. Zero erros é o critério.

**8. Capturas**: `browser_take_screenshot` (com `filename`). Se vier "janela oculta", meça por CDP e anexe as medidas.

**9. Teclado e mouse**: `browser_press_key` (Enter, Escape, setas, letras) e `browser_click` por `ref` do `browser_snapshot`. Confira com `scr()` e o `.gf` (foco) depois de cada passo.

## Bugs que valem caçar

Os que já apareceram aqui, por área (checklist completo em `checklist.md`):

- **Navegação**: Back que não volta, ou volta demais; A em Voltar que não sai; foco que cai do lado em vez de descer; cursor de um humano movendo o de outro.
- **Rótulos**: CPU aparecendo como P2; dica com botão errado para o controle em uso.
- **Estado órfão**: sair da Arena e entrar no Versus com resto de seleção; pad desconectado liberando a vaga errada.
- **Layout**: dica sobre botão; HUD sobre sprite; corte e scroll no celular; barra de rolagem piscando ao trocar de preview.
- **Combate**: golpe que encosta e não acerta; knockback que mata cedo; IA que não escolhe dificuldade.
- **Boot**: tela de carregamento eterna (TDZ, sintaxe, asset 404).

## Rodada Bugbot

Quando o autor pedir "rode o Bugbot em ciclo": (1) rode o subagente `bugbot` com `Diff: uncommitted changes`; (2) corrija só crítico e alto, com a menor mudança; (3) rode `check_syntax.py` e o fluxo afetado; (4) repita até limpar; (5) resuma o que achou, o que corrigiu e o que deixou de propósito (e por quê). Não "conserte" o que não for bug real.

## Relatório

Termine com: o que foi testado e como (script, receita, tela, dispositivo), o resultado, e o que **não** foi testado. Bug encontrado e não corrigido entra na lista.
