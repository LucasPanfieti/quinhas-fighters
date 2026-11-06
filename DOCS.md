# Quinhas Ball Fighters — documentação técnica

Documento de referência do jogo (v1.5.0). Serve para humanos e para IAs: descreve arquitetura, fluxo, dados, combate, input, opções e pipeline de assets. A fonte da verdade do runtime é o arquivo único `index.html`.

| Arquivo | Papel |
| --- | --- |
| `DOCS.md` | Referência técnica longa (este arquivo) |
| `docs/architecture.md` | Estrutura do `index.html`, símbolos, fluxo de telas |
| `docs/mechanics.md` | Golpes, Versus, Arena, IA e dificuldade, com números |
| `docs/controls.md` | Teclado, controle, celular e menus |
| `docs/visual-identity.md` | Cor, fonte, componentes, escala dos personagens |
| `docs/roadmap.md` | O que ainda não existe (Arcade etc.) |
| `.cursor/rules/` | Regras permanentes do agente |
| `.cursor/skills/` | Skills: `quinhas-fighters` (entrada), `-engineering`, `-game-design`, `-ui-art`, `-qa`, `-research` |
| `.cursor/skills/quinhas-fighters/decisions.md` | Decisões de design já aprovadas |

**Versus** é luta 2D no chão (Street Fighter, Mortal Kombat, Injustice): o golpe empurra e o palco tem paredes. **Arena** é Brawlhalla: estoque, plataformas e blast zone. Visual anime, compacto. Navegação no celular, no teclado, no mouse e no controle.

---

## 1. Visão geral

**Quinhas Ball Fighters** é um jogo de luta 2D no navegador. O Versus é melhor de 3. A Arena é estoque de 3 vidas. Roda sem build step: sirva a pasta por HTTP e abra `index.html`.

| Aspecto      | Detalhe                                                                                                     |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| Runtime      | Um único `index.html` (~CSS + HTML de UI + JS)                                                              |
| Render       | `<canvas id="c">` em resolução lógica **800×450**, buffer interno **1600×900** (`devicePixelRatio` fixo ×2) |
| Loop         | `requestAnimationFrame` + step fixo ~**60 Hz** (`16.67 ms`)                                                 |
| Áudio        | 100% sintetizado (Web Audio API), sem arquivos de som                                                       |
| Persistência | `localStorage`: `qf_au` (volumes / mute) e `qf_diff` (`e` / `n` / `h`)                                      |
| Idioma da UI | Português                                                                                                   |

Não há framework, bundler nem TypeScript. Mudanças de gameplay/UI entram direto em `index.html`.

---

## 2. Estrutura do repositório

```
quinhas-fighters/
├── index.html          # jogo inteiro (UI + engine)
├── DOCS.md             # este arquivo
├── README.md           # resumo + como rodar
├── .gitignore          # fontes locais / lixo de tools
├── assets/
│   ├── title.webp      # tela de título
│   ├── logo.png, favicon*.png
│   ├── bg.webp         # mapa 0 — Templo da Montanha
│   ├── bg2.webp        # mapa 1 — Colégio Leila Guedes
│   ├── bg3.webp … bg5.webp  # casas Quinhas / Junin / Bea
│   ├── faces/0..11.webp     # cards do roster (índices = ROSTER)
│   ├── faces/rnd.webp       # face do card Aleatório
│   ├── faces/rnd_body.webp  # silhueta corpo (preview do ?)
│   ├── stg/1.webp … 5.webp  # thumbs da seleção de estágio
│   └── spr/<id>/*.webp      # poses por personagem (ver §5)
├── tools/              # scripts Python de preparação de sprites (dev)
│   ├── build_sprites.py, slice.py, …
│   └── out/*.json      # metadados de poses (alguns versionados)
└── char-src/           # fontes locais (gitignored)
    ├── mapas/          # PNG brutos (mapa-3…); finais em assets/bg*.webp
    ├── quinhas-kun/
    ├── bea-trix/
    └── …
```

**O que sobe pro Git / produção:** `index.html`, `assets/`, `tools/*.py`, `tools/out/*.json`, docs.  
**O que fica local (gitignore):** `char-src/` (personagens + mapas fonte), `tools/__pycache__/`, imagens de teste em `tools/out/`.

---

## 3. Fluxo de telas (UI)

Overlays HTML dentro de `#stage`, acima do canvas. Visibilidade via `style.display` (`flex` / `none`). A função `scr()` detecta a tela atual.

```
loading → title → menu ⇄ sel → stg → (luta: intro/fight/end)
                      ⇄ hp (Controles)
                      ⇄ op (Opções)
              luta ⇄ pause ⇄ hp
```

| ID DOM     | Tela               | Notas                                                                      |
| ---------- | ------------------ | -------------------------------------------------------------------------- |
| `#loading` | Boot               | Barra de progresso; lista erros se asset falhar                            |
| `#title`   | Título             | Clique / qualquer tecla / botão de pad → menu                              |
| `#menu`    | Menu principal     | Versus (1-2), Arena (2-4), Controles, Opções, Título; Revanche / Trocar lutadores / Menu principal aparecem pós-partida |
| `#sel`     | Seleção de lutador | Grade `#grid` (12 + 3 em breve + Aleatório); previews `#fi`/`#fi2`/`#vs`   |
| `#stg`     | Seleção de cenário | 5 mapas + Aleatório                                                        |
| `#hp`      | Controles          | Tabela `#ct` preenchida por `buildHints`                                   |
| `#op`      | Opções             | Dificuldade (`#odrow`) + sliders de música/efeitos + mudo                  |
| `#pause`   | Pause (só em luta) | Continuar, Controles, Reiniciar, etc.                                      |
| `#pad`     | Gamepad virtual    | Só em `scr()==='game'` + classe `.on`                                      |
| `#pb`      | Botão Pausar       | Só durante a luta; em landscape mobile fica abaixo do cronômetro (não no canto) |
| `#prompts` | Dicas de navegação | Teclado ou ícones do pad (`padKind`). Some no toque (`pointer:coarse`)     |

### 3.1 Modos de seleção (`pendMode`)

- **`ai`:** um toque no card → IA escolhe oponente aleatório → `askStage('ai', id, opp)`. Card `?` resolve com `randFighter` na hora.
- **`2p`:** estado `s2` (`c` cursores, `lk` locks, `go` pronto). `AVall()` inclui `?`; confirmação resolve aleatório. Depois `askStage('2p', a, b)`.
- Após o estágio: `begin(m, a, b, stgIndex)` garante `loadLazy` dos 2 lutadores + `loadStage(stg)`, depois `beginNow` cria `p1`/`p2` e chama `startRound()`. Se o lazy load demorar >200 ms, reexibe `#loading` com “Carregando lutadores…”.

### 3.1.1 Layout do select (Injustice / responsivo)

| Viewport | Comportamento |
| -------- | ------------- |
| Desktop largo (`min-width:1000px` + `min-height:560px`) | Nomes no topo (`#fi`/`#fi2` nameplates); corpos idle grandes face a face atrás da grade; grade 8×2 na base; `#vs` escondido no 2P |
| Desktop estreito / baixo | 1P: só grade; 2P: faixa compacta `#vs` / `.pv` |
| Toque (`hover:none` + `pointer:coarse`) | **Sem** preview de corpo (`#fi`/`#fi2`/`#vs` `display:none !important`); botão legado `#b2p` sempre oculto (Versus e Arena são os dois modos do menu) |

Altura dos previews: `HM` (metros) → `scOf` → `P.sc` → `hsRatio` → CSS `--hs` (`height: calc(BASE * var(--hs))`, sem `max-width` que esmague o sprite). Aleatório (`?`) usa `RND_BODY` (`rnd_body.webp`, silhueta Eslepe) e `--hs` de `scOf("e")`.

`helpFrom` (`'menu'|'pause'`) faz o botão Voltar de Controles retornar à origem correta.

### 3.2 Pause landscape (mobile)

Em `@media (hover:none) and (pointer:coarse) and (orientation:landscape)`:

- `#pause[style*="flex"]` vira **CSS grid 2 colunas** (`display:grid !important` porque o JS seta `display:flex`). Continuar (`#pcont`) e Voltar ao título (`#ptit`) ocupam a linha inteira.
- `#pb` sai do canto superior direito e fica **centralizado abaixo do cronômetro**, para não cobrir o retrato do P2.

---

## 4. Loop principal e estados de luta

```text
loop(ts)
  padMenu()          // input de menus + uiTick
  step() × N         // física/IA a 60 Hz (accumulator)
  render()           // desenha frame
```

### 4.1 Variável `st` (estado de luta)

| Valor   | Comportamento                                                         |
| ------- | --------------------------------------------------------------------- |
| `menu`  | Fora de luta (ou pós-partida no menu HTML)                            |
| `intro` | Queda dos lutadores + VS splash / “Round N” / “Lute!”; `mt` countdown |
| `fight` | Input ativo, timer `tm` (60s), hits, projéteis                        |
| `end`   | Banner K.O./Tempo; se ninguém fechou o BO3, `rd++` e novo round       |

Pause: `paused=true` → `step()` retorna cedo (luta “congelada”, UI de pause aberta).

### 4.2 Regras da partida

- Melhor de 3 rounds (`wins` em cada `F`).
- Vitória do round: KO adversário, ou mais HP no timeout; empate de KO/timer dá win nos dois.
- Match over: 2 wins, ou tie-break no round 3.
- `LASTM = [mode, idA, idB, stg]` alimenta **Revanche**.

### 4.3 Efeitos globais de câmera

- `shake`, `freeze` (hitstop), `slow` + `zm` (zoom no KO).
- Chão lógico `G` muda por mapa (`MAPS[i].G`).

---

## 5. Personagens e sprites

### 5.1 IDs e roster

Ordem da grade = `ROSTER` + `LAB` + `assets/faces/<i>.webp`:

| Índice face | ID  | Nome        | Cor (`col`) | `HM` | Escala típica `P.sc` |
| ----------- | --- | ----------- | ----------- | ---- | -------------------- |
| 0           | `b` | Bea-Trix    | `#e0b45a`   | 1,60 | 0.537                |
| 1           | `r` | Cai-Ren     | `#8a9bb8`   | 1,75 | 0.587                |
| 2           | `c` | Cris-Chan   | `#f06ab8`   | 1,65 | 0.553                |
| 3           | `e` | Eslepe-San  | `#d98a3a`   | 1,85 | 0.621                |
| 4           | `g` | Giu-Lee     | `#a15cf0`   | 1,65 | 0.553                |
| 5           | `k` | Junin-Kai   | `#f08a24`   | 1,85 | 0.621                |
| 6           | `u` | Luan-Zin    | `#2fbf5a`   | 1,70 | 0.570                |
| 7           | `l` | Mestre-Leco | `#e03a3a`   | 1,75 | 0.587                |
| 8           | `q` | Quinhas-Kun | `#3d6bff`   | 1,75 | 0.587                |
| 9           | `s` | Samu-Kan    | `#e8c84a`   | 1,75 | 0.587                |
| 10          | `t` | Taka-Shin   | `#19c6c0`   | 1,70 | 0.570                |
| 11          | `y` | Yas-Mine    | `#c45a8c`   | 1,60 | 0.537                |

`CH[id] = { n, P, col }` é montado **depois** do load das imagens.  
`HM` (altura em metros por id) + `SC`/`REF_M` alimentam `scOf(id)` → `P.sc` na luta.  
`hsRatio(sc)` normaliza altura nas UIs de seleção (maior `sc` do elenco = 1.0 → CSS `--hs`).

Slots **em breve** (índices 12–14): cards sem `data-id`, `disabled`, arte em grayscale. Slot **Aleatório** (`data-id="?"`): último da grade.

### 5.2 Objeto `SPR` e pastas `assets/spr/<id>/`

Cada personagem tem um bloco em `SPR` com URLs das poses + metadados `m`:

```text
id  idle          wk  walk         cr  crouch
jp  jump          pu  punch        ki  kick
cp  soco agachado ck  chute agachado
ap  soco aéreo    ak  chute aéreo
bl  block         ht  hurt         hd  cast Esfera de Ki
hb  sprite da esfera (meta dx,dy,hx)   fa  fall
ko  nocaute       vi  vitória
```
(cp/ck/ap/ak hoje só no Quinhas-Kun; outros caem no pu/ki.)

Cada entrada em `m[pose]` tipicamente:

- `w`, `h` — tamanho do quadro
- `ax` — âncora X (pés/tronco); desenho usa `-ax*sc` no eixo X
- Em `hb`: `dx`, `dy`, `hx` — offset de spawn / hold da esfera

Cache-bust: query `?v=N` nas URLs (incrementar ao trocar arte).

### 5.3 Boot / load

1. `LOAD.total` ≈ `Object.keys(SPR).length * 2 + 1` (barra só cobre o boot: idle + nomes + `bg.webp`).
2. `ld(SPR.*)` carrega **só a pose `id` (parado)** via `load()`; as demais poses entram em `P._lz` (Image sem `src`) e sobem depois com `loadLazy(P)`.
3. `Promise.all` no boot: `ld` de todos os personagens + `nameLoads` + `bg.webp`. Fundos `bg2`…`bg5` usam `img.dataset.src` e só resolvem `src` em `loadStage(i)`.
4. Atribui `sc`, `pf` (face Image) e preenche `CH`.
5. Instancia `p1`/`p2` dummy, mostra título, inicia `loop`.
6. Se algum arquivo falhar → tela de erro listando paths (lembrar: pasta `assets/` precisa acompanhar o HTML).

**Lazy load (após o boot):**

| Quando | O quê |
| ------ | ----- |
| `askStage` | `loadLazy` dos dois lutadores escolhidos |
| `pointerenter` no card de mapa (`#stgrid .stc`, exceto Aleatório) | `loadStage(+dataset.i)` |
| `begin` | `Promise.all([loadLazy(P1), loadLazy(P2), loadStage(stg)])` → `beginNow` |

`loadLazy` / `loadStage` cacheiam a Promise em `P._lp` / `im._lp` (não recarregam). `beginBusy` evita double-tap abrindo duas lutas.

**Armadilha conhecida:** `buildHints` / `hintTick` podem chamar `selInfo()` antes de `CH` existir. Por isso `hintTick` usa `try{selInfo()}catch`. Não chamar `selInfo` “puro” no boot sem esse cuidado.

---

## 6. Classe `F` (lutador)

```js
new F(nome, P, startX, cor);
```

### 6.1 Estado importante (`reset`)

`x,y,vy,hp,gh,atk,t,stun,kb,blk,ko,mv,cr,hcd,wp,land,jt,hf,tr,cur,landed,face,wins,plan,pt`

- `gh` — “ghost HP” (barra amarela atrasada).
- `hcd` — cooldown da Esfera de Ki (~80 frames após disparo).
- `face` — `1` direita / `-1` esquerda (sempre olha o oponente quando livre).
- `plan`/`pt` — só usados pela IA.

### 6.2 `up(input, opponent)` — um tick

Prioridade aproximada:

1. KO → animação / empurrão.
2. Stun → knockback, sem controle.
3. Ataque ativo (`atk` ∈ `p|k|h`) → frames de startup/active/recovery (`ATK`).
4. Livre: face, block, crouch, walk, jump, iniciar ataque.

Física: gravidade `vy += 0.85`, chão `y=0`, clamp X `[30, W-30]`.

### 6.3 Ataques `ATK`

| Key | Significado  | Campos relevantes                                                                                            |
| --- | ------------ | ------------------------------------------------------------------------------------------------------------ |
| `p` | Soco         | `s` startup, `a` active, `n` duração total, `d` dano, `r` alcance, `st` stun, `kb` knockback, `hy` altura FX |
| `k` | Chute        | maior alcance/dano                                                                                           |
| `h` | Esfera de Ki | no frame `s` chama `fireball`; hitbox corpo `r:0` (dano via projétil)                                        |

Hit: `strike` enfileira em `HQ`; `flushHits()` aplica `hurt` depois (evita ordem P1/P2 no mesmo frame).

**Versus (`F.hurt`):** `kb = face * a.kb`. Empurra no chão e para na parede do palco. Não há blast zone.

**Arena (`AF.hurt`):** `lost = 1 - hp/100`, `base = 7` na esfera e `a.kb` no resto, `kx = face * base * (0.55 + lost * 0.85)`. O pop vertical (`base * 0.16 + lost * base * 0.5`) só sai se passar de 2.6, com teto 13. Dano baixo escorrega; perto de 0 é que mata para fora. A mesma curva vale para jogador e CPU.

**Block:** `hurt` com `blk` → ~15% do dano, stun curto, FX de bloqueio.  
**KO:** `hp<=0` → `ko`, slow-mo no Versus, SFX.

### 6.4 Desenho `draw` / sombra

Escolhe pose `pz` conforme estado; aplica offsets `tx/ty/rot/sx/sy` (keyframes `kf`).  
Trail de ataque em `tr`.  
Sombra usa amostragem de pés (`foot`) ou blobs sob jump/ki.

Escala de desenho: `sc = P.sc || SC` com `SC = 0.587` (referência). Alcance de golpe escala com `P.sc`.

---

## 7. Projéteis (Esfera de Ki)

Array global `PJ`. `fireball(o)` spawna na âncora `hb` do caster.

- Velocidade: `dir * 8` px/frame.
- Colisão oponente: `|dx|<34` e não KO → `hurt` com `ATK.h`.
- Colisão esfera×esfera opostas: ambas morrem + sparks.
- Cooldown do caster: `hcd=80`.

---

## 8. IA (`ai` e `aiArena`)

`ai(me, o)` controla o `p2` quando `mode==='ai'`. `aiArena(me)` controla cada slot `ai` da Arena. As duas leem `aiTune()`.

`DIFF` é `e` (Fácil), `n` (Normal) ou `h` (Difícil), salvo em `qf_diff`. O padrão é Normal. `aiTune()` devolve `wait` (tempo entre planos), `brave` (chance de atacar), `blk` e `dodge`. Dificuldade não muda dano nem knockback.

Na tela `#op`, `#odrow` cicla com clique ou seta esquerda/direita. Ainda não há seletor na seleção de personagem.

Não é pathfinding. O retorno tem o mesmo shape do jogador: `{l,r,u,d,p,k,h,b}`.

---

## 9. Input

### 9.1 Teclado (luta)

| Ação         | P1                                    | P2       |
| ------------ | ------------------------------------- | -------- |
| Mover        | WASD                                  | Setas    |
| Soco         | J                                     | Numpad 4 |
| Chute        | I                                     | Numpad 8 |
| Esfera de Ki | L                                     | Numpad 6 |
| Defesa       | Espaço                                | Numpad 0 |
| Especial     | K (UI “Em breve”; sem efeito de luta) | Numpad 5 |
| Pause        | Esc / P                               | Esc / P  |
| Mute global  | M                                     | M        |

Menus: setas/WASD navegam, Enter confirma, Esc volta. Em seleção 2P há bindings dedicados (`s2in`).

### 9.2 Gamepad (`gin`)

Mapeamento **intencional estilo PlayStation / face buttons remapeados**:

| Ação           | Botão padrão (índice) | Ícone PS na UI |
| -------------- | --------------------- | -------------- |
| Soco           | 2                     | □              |
| Chute          | 3                     | △              |
| Esfera de Ki   | 1                     | ○              |
| Defesa         | 5 (R1)                | R1             |
| Pulo (Versus)  | 12 / stick ↑ **ou** 0 (✕/A) | ✕ também pula |
| Especial       | 4 (L1/LB) — UI “Em breve” | L1         |
| Confirmar menu | 0                     | ✕              |
| Voltar menu    | 1                     | ○              |
| Start/Pause    | 9                     | —              |

D-pad 12–15 + eixos 0/1.  
`padKind(g)`: DualShock/DualSense/etc. → ícones PS (`p`); senão Xbox (`x`).

### 9.3 Pad virtual mobile (`#pad`)

- Aparece em luta se `uiTick` liga `.on` (tela `game`). Em dispositivos coarse o CSS já prepara o layout.
- Analógico `#stick` → `keys.vL/vR/vU/vD` (deadzone + vetor unitário).
- Botões `.b[data-k=vP|vK|vH|vB]` → mesmas flags usadas por `in1`.
- Botão Especial: classe `.soon`, **sem** `data-k` (inerte).
- Tamanho: CSS `--bs` / `.acts --r` (valores clamp por orientação).

`in1` combina teclado + virtual + `gpad(0)`.  
`in2` teclado P2 + `gpad(1)` (sem stick virtual — stick é só P1).

### 9.4 Dicas dinâmicas

`buildHints(ks)` atualiza `#prompts` e células `#ct td[data-ct][data-p]` conforme:

- teclado (`KB`), ou
- pad (`gI` + `XC`/`PC`), ou
- coarse → força ícones estilo PS mesmo sem controle físico.

---

## 10. Áudio

Tudo em código (`tone`, `nz`, trilhas `ML`/`TRK`/`PR`).

- Canais: master / música / SFX; ducking durante luta.
- Unlock: primeiro gesture (`aUnlock`) por política do browser.
- `#om` e `#os` são sliders 0–100 (`AU.vol`, passo de 5% no teclado/controle). `#omu` alterna o mudo. `#odrow` é a dificuldade da CPU.
- `ANNOUNCER=false` desliga `speechSynthesis` (código ainda existe).

---

## 11. Canvas / render

Ordem típica em `render()`:

1. Clear + shake/zoom transform
2. Background (`curBg` ou `bg` no menu)
3. Partículas de estágio, sombras, lutadores, projéteis, sparks
4. Vignette + barras de vida (`bar`) + timer
5. Overlays intro/end (`drawVs`, `banner`)

HUD HTML (menus) é separado do canvas.

---

## 12. CSS / mobile

- Fontes: **Dela Gothic One** + **Rajdhani** (Google Fonts).
- Safe areas: `--safe-t/r/b/l`.
- Touch: em coarse, `#app`/`body` evitam scroll (`position:fixed`, overflow hidden — ver media queries).
- Select Injustice: `@media (min-width:1000px) and (min-height:560px)` — ver §3.1.1; reafirmação de `#fi`/`#fi2` perto do fim do CSS (sobrescreve `right:2%` legado).
- Estágio landscape: `#stgrid` em row; portrait empilha cards.
- Wedges laterais (`::before/::after` nos overlays) somem em coarse para não “sujar” o mapa.

---

## 13. Pipeline de sprites (`tools/`)

Fluxo típico de arte (dev local):

1. Pasta fonte por personagem em `char-src/<nome>/` (ex.: `char-src/quinhas-kun/`) com tiras de poses — **não versionada**.
2. `tools/slice.py` — recorta frames.
3. `tools/build_sprites.py` — normaliza altura/âncora, empacota atlas, grava `tools/out/<id>.json` e `assets/spr/<id>/`.
4. Metadados `w/h/ax/...` são **copiados/atualizados** no objeto `SPR` dentro de `index.html` (hoje o jogo usa webps por pose, não o atlas sheet em runtime — conferir o que o build atual gera vs. o que o HTML referencia).

Ao adicionar personagem novo:

1. Arte → `assets/spr/<id>/` + face em `faces/`.
2. Entrada em `SPR`, `ROSTER`/`LAB`, load em `Promise.all`, `CH`, `sc`.
3. Incrementar `?v=` das URLs mexidas.

---

## 14. Checklist para quem for editar

| Quero…                             | Onde                                                |
| ---------------------------------- | --------------------------------------------------- |
| Mudar dano/frames de golpe         | `ATK`                                               |
| Mudar controles teclado/luta       | `in1`/`in2` + `KB`                                  |
| Mudar botões do pad físico         | `gin`                                               |
| Mudar layout/tamanho do pad mobile | CSS `#pad`, `--bs`, `.acts --r`                     |
| Mudar pause landscape              | media query coarse+landscape `#pause…` / `#pb`      |
| Lazy load de sprite/mapa           | `loadLazy`, `loadStage`, `ld` (`id` eager / resto `_lz`) |
| Novo mapa                          | fonte em `char-src/mapas/`, depois `assets/bg*.webp` + thumb `#stgrid` + `MAPS` |
| Texto de versão                    | `#tver`, `#ver` (manter alinhado ao ship)           |
| Layout do select Injustice         | media `1000×560` + `#fi`/`#fi2`/`#grid` / `--hs`  |
| Volumes default                    | `AU.vol` + `qf_au`                                  |
| Dificuldade da CPU                 | `DIFF`, `aiTune`, `qf_diff`, `#odrow`               |
| Comportamento da IA                | `ai` (Versus) e `aiArena` (Arena)                   |
| Animação de pose                   | `F.draw` + arquivos em `SPR`                        |

---

## 14.1 Modo Arena (2–4 lutadores · v1.5.0)

Modo estilo Brawlhalla: stock, mapa com plataformas e blastzones. Vive em **caminho separado** do 1v1 (`p1`/`p2`, `step`, `begin` ficam intactos). Código no bloco `ARENA` perto do fim do `<script>` (antes de `loop`) + classe `AF` logo depois de `F`.

### Regras

- 2 a 4 lutadores, **todos contra todos** (friendly fire sempre on), **3 vidas** (`ARENA_LIVES`).
- Perde 1 vida ao **zerar HP** ou **sair da blastzone** (`ARENA.blast`). Respawn com HP 100, hover ~0,75 s e i-frames (~3 s, pisca).
- Vence o **último com vida**; cap de **5:00** (`ARENA_TIME`) → mais vidas; empate de vidas = **Empate** (sem sudden death).
- **Knockback cresce com o HP perdido** (`AF.hurt`, fórmula no §6.3). Esfera de Ki usa `base` 7. No meio da vida, do centro da ilha, o chute não deve matar.
- **1 pulo duplo** (`vy -10` no chão, `-9.6` no ar; gravidade `0.5`, queda máx. `12`; `SPD = 3.2`). Teclado: `W`/↑; pad: só ✕/A (stick ↑ não pula). `K`/Num5/L1 = especial em breve. ↓ em plat soft atravessa; sem air dodge/wall jump.
- Suicídio (cai sem hit recente, `lastT`≤0) = −1 vida sem crédito de KO; senão `lastBy.kos++`.

### Mapa — Ilhas do Céu

`assets/arena.webp` (1600×900) + thumb `assets/stg/arena.webp`. **Não entra em `MAPS`** (carrega via `loadArena`). Colisão em `ARENA.surf`: chão principal (`y:289`, hard) + 2 plats **soft** (`y:146`). Fundo é só visual. Sprites desenhados a `ARK=0.27` (`P = Object.create(P0); P.sc *= ARK`).

### Seleção

`openLobby(..., "arena")` manda o desktop para `a4Open` e o celular (`IS_TOUCH`, ou `?touch=1`) para `#almob`.

**Desktop** (`#sel`, `data-m="arena"`, estado `A4`): até 4 vagas. Cada teclado (máx. 2) ou controle (até 4) entra apertando um botão e move o próprio cursor (P1 laranja, P2 azul, P3 verde, P4 rosa). Nada começa pré-selecionado. `+ CPU` é `I` / Num8 / Y; `− CPU` é `L` / Num6 / X. Sozinho, já entra uma CPU. Começar exige humanos confirmados e 2+ lutadores. A em Voltar sai da tela (`a4Leave`). Cursores no mesmo card misturam a cor; confirmar é aro e lavagem, sem check.

**Celular** (`#almob`, chips `#amc`): escolhe 1, 2 ou 3 inimigos e o próprio lutador. O resto é CPU sorteada. Sem a tela de 4 vagas.

**Versus** (`openSel("vs")`, `s2.vs`): a grade é a clássica. O preview diz "Pressione para entrar" até alguém entrar (`vsIn`). Sozinho, o P1 escolhe o seu e depois o da CPU (`data-cpu`, não P2). Dois humanos viram `2p` e seguem para o cenário. Dispositivos em `VDEV` (`in1` / `in2`). No celular: toque no seu lutador e depois no adversário, sem preview de corpo.

Controles tem abas Versus e Arena (`hpTab`). No toque, `#prompts` some.

Humano não vira sozinho para o inimigo: `AF` só muda `face` quando ele anda. A CPU olha o alvo.

### Funções principais

| Função | Papel |
| ------ | ----- |
| `AF` | `F` + física de plataforma (`wy`, `on`, `sup`, `jc`, `drop`, `inv`, `rsp`, `lives`, `kos`) |
| `devIn(dev, noJump)` | input do slot (`k1`/`k2`/`pN`). Teclado: `W`/↑ pulam nos dois modos. **Arena** (`noJump` falso): pad só ✕/A pula (stick ↑ ignorado). **Versus** (`noJump` true): pad pula com stick/↑ **ou** ✕/A (`gin`) |
| `aiArena(me)` | IA: alvo mais próximo, recuperação, sobe/desce plats, não cai sozinha |
| `beginArena(cfg)` / `beginArenaNow` | carrega lazy + `arena.webp`, cria `fighters[]`, `st="arena"` |
| `stepArena` | `ast` = `intro` → `fight` → `end`; chama `up`, `flushHits`, `updArenaPJ`, `sepArena`, `checkBlast` |
| `drawArenaWorld` / `drawArenaHud` | render (lutadores, 4 cards com vidas/HP, timer, indicador fora da tela) |
| `LASTA` | config da última Arena (Revanche / Reiniciar) |

`cfg` = `[{ t:'human'|'ai', dev, cid, slot }]`. Durante a luta `scr()` devolve `game` (pausa por qualquer humano: Esc/P/Start).

## 15. Glossário rápido

| Termo   | Significado                                           |
| ------- | ----------------------------------------------------- |
| `P`     | Pacote de imagens + `m` + `sc` + `pf` do personagem   |
| `pz`    | Pose atual (string chave de `SPR`)                    |
| `SC`    | Escala de referência 0.587                            |
| `G`     | Y do chão no canvas lógico                            |
| `HQ`    | Fila de hits do frame                                 |
| `PJ`    | Projéteis de Ki                                       |
| `LASTM` | Última luta (revanche)                                |
| `LASTA` | Última Arena (revanche)                               |
| `AF`    | Lutador da Arena (`F` + plataforma/stock)             |
| `DIFF`  | Dificuldade da CPU: `e` Fácil, `n` Normal, `h` Difícil |
| `gf`    | Classe “foco” de navegação por teclado/pad nos botões |

---

## 16. Como rodar / publicar

**Local:** servir a pasta (ex. `python -m http.server`) e abrir no browser. Abrir o `file://` do HTML pode falhar em alguns browsers por CORS/load de assets — preferir HTTP.

**Produção:** publicar `index.html` + pasta `assets/` juntos. Versão exibida na UI: **v1.5.0** (atualizar strings ao shipar).

**Git:** commits só com o que for pedido; `.gitignore` impede pastas fonte e lixo de `tools/out` (exceto `*.json`).

---

_Última revisão alinhada ao `index.html` v1.5.0 (Opções com dificuldade, knockback da Arena, lobbies de Versus e Arena). Se o código divergir deste doc, o código manda — atualize esta página._
