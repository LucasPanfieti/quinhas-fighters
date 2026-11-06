# Arquitetura

Descrição do que existe em `index.html`. Detalhe fino e tabelas longas estão em [DOCS.md](../DOCS.md). Quando o código mudar, mude aqui.

## Visão

| Item | Fato |
| --- | --- |
| Entrega | `index.html` (~11,5 mil linhas) + `assets/`. Sem build, sem framework, sem dependência npm |
| Publicação | Site estático (GitHub Pages; existe `.nojekyll`) |
| Render | `<canvas id="c">`, resolução lógica **800×450** (`W`, `H`), buffer 1600×900 |
| Loop | `loop(ts)`: `lobbyTick()`, `padMenu()`, `step()` a 60 Hz fixo (acumulador de 16,67 ms), `render()` |
| Externo | Só a fonte do Google Fonts (Dela Gothic One, Rajdhani) |
| Persistência | `localStorage`: `qf_au` (volumes, mudo), `qf_diff` (`e`/`n`/`h`) |
| Áudio | Sintetizado em Web Audio (`AU`, `aInit`, `tone`), sem arquivo de som |

## Camadas do arquivo

1. **CSS** (topo). Variáveis em `:root`, overlays por `#id`, media queries para toque, telas baixas e paisagem.
2. **HTML dos overlays** dentro de `#stage`: `#loading`, `#title`, `#menu`, `#sel`, `#stg`, `#alobby`, `#hp` (Controles), `#op` (Opções), `#pause`, `#pad` (controle virtual), `#prompts`.
3. **Script único**, em ordem (o que vem depois pode usar o que vem antes; o inverso dá TDZ):

| Bloco | Símbolos |
| --- | --- |
| Assets | `SPR` (URLs por pose), `W`, `H`, `G`, `bg*`, `ld`, `loadLazy`, `loadStage` |
| Input | `gin` (pad), `KB` (tabela de dicas), `IN` (`kb`/`pad`), `padKind`, `gI`, `buildHints`, `hintTick` |
| Menu | `scr()` (tela atual), `LS` (itens focáveis por tela), `press(k)`, `padMenu`, `uiConfirm`, `uiBack`, `selStackBack`, `holdMenuPad` |
| Entrada de luta | `in1`, `in2`, `devIn`, `VDEV` |
| Áudio e opções | `AU`, `aSave`, `DIFF`, `aiTune`, `cycleDiff`, `updOpt` |
| Combate Versus | `ATK`, `PJ`, `fireball`, `class F`, `flushHits`, `ai` |
| Arena | `class AF extends F`, `ARENA`, `ARK`, `aiArena`, `stepArena`, `checkBlast` |
| Fluxo | `MAPS`, `ROSTER`/`LAB`, `CH`, `startRound`, `beginNow`, `begin`, `beginArena`, `askStage` |
| Seleção | `s2` (Versus), `A4` e `a4*` (Arena desktop), `openSel`, `openLobby`, `a4Open`, `a4Leave` |
| Loop | `step()`, `render()`, `loop()` |

## Estado global importante

- `st`: `menu` / `intro` / `fight` / `end` / `arena`. `paused`.
- `mode`: `ai` ou `2p` (Versus). `p1`, `p2` (Versus). `fighters[]`, `ast` (`intro`/`fight`/`end`) na Arena.
- `CH[id] = { n, P, col }` montado **depois** do load das imagens. Chamar `selInfo()` antes disso dá erro (por isso `hintTick` usa `try/catch`).
- `pendMode` (`ai`, `2p`, `arena`), `s2` (cursores, locks, dispositivos, `hum`), `A4` (4 vagas), `a4Focus` (`grid`/`party`/`acts` e o dispositivo dono).
- `IS_TOUCH` decide o lobby da Arena (celular x desktop). `?touch=1` força para teste.

## Versus x Arena

Caminhos separados que compartilham a classe `F`.

| | Versus | Arena |
| --- | --- | --- |
| Lutador | `F` | `AF extends F` (plataforma, estoque, `wy`, `jc`, `inv`) |
| Passo | `step()` ramo `fight` | `stepArena()` |
| Início | `begin` → `beginNow` → `startRound` | `beginArena` → `beginArenaNow` |
| Golpe | `F.hurt` (`kb` fixo) | `AF.hurt` (cresce com o HP perdido) |
| IA | `ai` | `aiArena` |
| Fim | melhor de 3 rounds | último com vida, 3 vidas, 5:00 |
| Cenário | `MAPS` (4 mapas + aleatório) | `ARENA` (Ilhas do Céu) |

## Fluxo de telas

```
loading → title → menu ⇄ sel (Versus) → stg → luta
                  menu ⇄ sel (Arena desktop, a4*) → luta
                  menu ⇄ alobby (Arena celular) → luta
                  menu ⇄ hp (Controles) · op (Opções)
                  luta ⇄ pause ⇄ hp
```

Visibilidade é `style.display` (`flex`/`none`); `scr()` lê qual está aberta e diz ao `press`/`padMenu` como navegar.

## Assets e ferramentas

- `assets/spr/<id>/<pose>.webp`: uma imagem por pose. `assets/faces/` (cards), `assets/names/` (nomes estilizados), `assets/stg/` (miniaturas de mapa), `assets/ui/` (ícones do controle virtual), `bg*.webp`, `arena.webp`, `title.webp`, `logo.*`, `favicon*`.
- Pose por id: `id wk cr jp pu ki bl ht hd hb fa ko vi cp ck ap ak cb ab wb` (nem todo personagem tem todas; o código checa `P.xx`).
- Altura real: `HM` (metros) → `scOf` → `P.sc`. Ver `docs/visual-identity.md`.
- `tools/` (Python, Pillow/numpy): `slice.py` (recorte com chroma key), `build_sprites_dir.py` (importa poses soltas), `build_sprites.py`, `match_luan_colors.py`, `restore_all.py`, `mk_test.py`. Caminhos absolutos da máquina do autor. `tools/out/*_poses.json` são versionados; o resto é lixo de teste.
- `char-src/` é fonte local, gitignored.

## Testes

Não há suíte automatizada nem `package.json`. A verificação é manual e por browser; o procedimento está em `.cursor/skills/quinhas-qa/`.
