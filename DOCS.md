# Quinhas Ball Fighters — documentação técnica

Documento de referência do jogo (v1.3.5+). Serve para humanos e para IAs: descreve arquitetura, fluxo, dados, combate, input, áudio e pipeline de assets. A fonte da verdade do runtime é o arquivo único `index.html`.

---

## 1. Visão geral

**Quinhas Ball Fighters** é um fighting game 2D no navegador (estilo arcade, melhor de 3). Roda sem build step: abrir `index.html` (ou servir a pasta por HTTP) basta.

| Aspecto      | Detalhe                                                                                                     |
| ------------ | ----------------------------------------------------------------------------------------------------------- |
| Runtime      | Um único `index.html` (~CSS + HTML de UI + JS)                                                              |
| Render       | `<canvas id="c">` em resolução lógica **800×450**, buffer interno **1600×900** (`devicePixelRatio` fixo ×2) |
| Loop         | `requestAnimationFrame` + step fixo ~**60 Hz** (`16.67 ms`)                                                 |
| Áudio        | 100% sintetizado (Web Audio API), sem arquivos de som                                                       |
| Persistência | `localStorage` chave `qf_au` (volumes / mute)                                                               |
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
│   ├── faces/0..11.webp
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
                      ⇄ op (Áudio)
              luta ⇄ pause ⇄ hp
```

| ID DOM     | Tela               | Notas                                                                      |
| ---------- | ------------------ | -------------------------------------------------------------------------- |
| `#loading` | Boot               | Barra de progresso; lista erros se asset falhar                            |
| `#title`   | Título             | Clique / qualquer tecla / botão de pad → menu                              |
| `#menu`    | Menu principal     | Um jogador, Versus, Controles, Áudio, Título; Revanche aparece pós-partida |
| `#sel`     | Seleção de lutador | Grade `#grid`; previews `#fi`/`#fi2` (1P) ou `#vs` (2P)                    |
| `#stg`     | Seleção de cenário | 5 mapas + Aleatório                                                        |
| `#hp`      | Controles          | Tabela `#ct` preenchida por `buildHints`                                   |
| `#op`      | Áudio              | Cicla música / SFX / mute                                                  |
| `#pause`   | Pause (só em luta) | Continuar, Controles, Reiniciar, etc.                                      |
| `#pad`     | Gamepad virtual    | Só em `scr()==='game'` + classe `.on`                                      |
| `#pb`      | Botão Pausar       | Só durante a luta                                                          |
| `#prompts` | Dicas de navegação | Teclado vs ícones de pad                                                   |

### 3.1 Modos de seleção (`pendMode`)

- **`ai`:** um toque no card → IA escolhe oponente aleatório → `askStage('ai', id, opp)`.
- **`2p`:** estado `s2` (`c` cursores, `lk` locks, `go` pronto). Cada jogador confirma; depois `askStage('2p', a, b)`.
- Após o estágio: `begin(m, a, b, stgIndex)` cria `p1`/`p2` e chama `startRound()`.

`helpFrom` (`'menu'|'pause'`) faz o botão Voltar de Controles retornar à origem correta.

### 3.2 Pause landscape (mobile)

Em `@media (hover:none) and (pointer:coarse) and (orientation:landscape)`, `#pause[style*="flex"]` vira **CSS grid 2 colunas** (`display:grid !important` porque o JS seta `display:flex`). Continuar (`#pcont`) e Voltar ao título (`#ptit`) ocupam a linha inteira.

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

| Índice face | ID  | Nome        | Cor (`col`) | Escala típica `P.sc` |
| ----------- | --- | ----------- | ----------- | -------------------- |
| 0           | `b` | Bea-Trix    | `#e0b45a`   | 0.537                |
| 1           | `r` | Cai-Ren     | `#8a9bb8`   | 0.587                |
| 2           | `c` | Cris-Chan   | `#f06ab8`   | 0.553                |
| 3           | `e` | Eslepe-San  | `#d98a3a`   | 0.621                |
| 4           | `g` | Giu-Lee     | `#a15cf0`   | 0.553                |
| 5           | `k` | Junin-Kai   | `#f08a24`   | 0.621                |
| 6           | `u` | Luan-Zin    | `#2fbf5a`   | 0.570                |
| 7           | `l` | Mestre-Leco | `#e03a3a`   | 0.587                |
| 8           | `q` | Quinhas-Kun | `#3d6bff`   | 0.587                |
| 9           | `s` | Samu-Kan    | `#e8c84a`   | 0.587                |
| 10          | `t` | Taka-Shin   | `#19c6c0`   | 0.570                |
| 11          | `y` | Yas-Mine    | `#c45a8c`   | 0.537                |

`CH[id] = { n, P, col }` é montado **depois** do load das imagens.  
`hsRatio(sc)` normaliza altura nas UIs de seleção (maior `sc` do elenco = 1.0).

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

1. `LOAD.total` ≈ personagens×8 + 2 fundos (estimativa da barra).
2. `Promise.all` carrega poses via `ld(SPR.*)` + `bg`…`bg5`.
3. Atribui `sc`, `pf` (face Image) e preenche `CH`.
4. Instancia `p1`/`p2` dummy, mostra título, inicia `loop`.
5. Se algum arquivo falhar → tela de erro listando paths (lembrar: pasta `assets/` precisa acompanhar o HTML).

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

**Block:** `hurt` com `blk` → ~15% do dano, stun curto, FX de bloqueio.  
**KO:** `hp<=0` → `ko`, slow-mo, SFX, música de luta para.

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

## 8. IA (`ai(me, o)`)

Só controla `p2` quando `mode==='ai'`.

- A cada `pt` frames escolhe `plan` por distância + RNG: aproximar (`ap`), recuar, soco, chute, block, jump, hadouken.
- Reações: bloqueio ocasional se oponente ataca perto ou se há projétil vindo.
- Retorna o mesmo shape de input que o jogador: `{l,r,u,d,p,k,h,b}`.

Não é pathfinding — máquina de estados simples o suficiente para “parecer viva”.

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
- Opções ciclam `0 → 0.25 → 0.5 → 0.75 → 1`.
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
| Mudar pause landscape              | media query coarse+landscape `#pause…`              |
| Novo mapa                          | fonte em `char-src/mapas/`, depois `assets/bg*.webp` + thumb `#stgrid` + `MAPS` |
| Texto de versão                    | `#tver`, `#ver`                                     |
| Volumes default                    | `AU.vol` + `qf_au`                                  |
| Comportamento da IA                | função `ai`                                         |
| Animação de pose                   | `F.draw` + arquivos em `SPR`                        |

---

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
| `gf`    | Classe “foco” de navegação por teclado/pad nos botões |

---

## 16. Como rodar / publicar

**Local:** servir a pasta (ex. `python -m http.server`) e abrir no browser. Abrir o `file://` do HTML pode falhar em alguns browsers por CORS/load de assets — preferir HTTP.

**Produção:** publicar `index.html` + pasta `assets/` juntos. Versão exibida na UI: **v1.3.5** (atualizar strings ao shipar).

**Git:** commits só com o que for pedido; `.gitignore` impede pastas fonte e lixo de `tools/out` (exceto `*.json`).

---

_Última revisão alinhada ao código em `index.html` (v1.3.5: Quinhas Ball Fighters, logo e título). Se o código divergir deste doc, o código manda — atualize esta página._
