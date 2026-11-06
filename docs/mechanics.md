# Mecânicas

O que o jogo faz hoje, lido do código. Itens planejados ficam em [roadmap.md](roadmap.md).

## Golpes (`ATK`)

Quadros a 60 Hz. `s` startup, `a` ativo, `n` duração, `d` dano, `r` alcance, `st` stun, `kb` empurrão, `hy` altura do efeito.

| Golpe | Chave | s | a | n | d | r | st | kb |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Soco | `p` | 4 | 9 | 18 | 6 | 158 | 12 | 4 |
| Chute | `k` | 8 | 10 | 30 | 11 | 175 | 18 | 8 |
| Soco agachado | `cp` | 3 | 10 | 18 | 5 | 120 | 12 | 3 |
| Chute agachado | `ck` | 5 | 12 | 26 | 9 | 165 | 16 | 6 |
| Soco aéreo | `ap` | 2 | 10 | 16 | 5 | 115 | 10 | 3 |
| Chute aéreo | `ak` | 4 | 11 | 22 | 9 | 155 | 14 | 6 |
| Esfera de Ki | `h` | 16 | 0 | 38 | 9 | 0 (projétil) | 16 | 6 |

- O alcance real usa o sprite da pose (`m.w - m.ax`) quando existe e escala com `P.sc` (`F.strike` no Versus, `AF.swing`/`AF.reaches` na Arena). O golpe acerta quando o desenho encosta.
- Hit entra em `HQ` e `flushHits()` aplica `hurt` depois, para a ordem P1/P2 não decidir o frame.
- Bloqueio (`blk`): 15% do dano, stun 8, empurrão curto. Acerto: hitstop (`freeze = 3`), tremor de tela, faíscas.
- **Esfera de Ki** (`fireball`): sai da âncora `hb` da pose `hd`, 8 px/quadro, cooldown `hcd = 80`. Duas esferas opostas se anulam. Só dispara no chão.

## Versus

- 1–2 jogadores. Sozinho, o P1 escolhe o próprio lutador e depois a CPU. Dois humanos viram `2p`.
- Melhor de 3 rounds. Round de 60 s. Vence quem zera o HP do outro; no tempo, quem tem mais HP; empate dá vitória aos dois.
- HP 100 por round. Pulo `vy = -16.4`, gravidade `0.85`. Tela com paredes (`x` preso a `[30, W-30]`). Sem blast zone.
- `F.hurt`: empurrão fixo `kb = face * a.kb`. KO tem slow-motion e zoom.
- Cenários (`MAPS`): Colégio Leila Guedes, Casa do Quinhas, Casa do Junin, Casa da Bea, mais "Aleatório". O Templo da Montanha (`bg`) existe e fica oculto.
- Revanche usa `LASTM = [mode, idA, idB, stg]`.

## Arena

- 2–4 lutadores, todos contra todos, **3 vidas** (`ARENA_LIVES`), cap de **5:00** (`ARENA_TIME`). Último vivo vence; no tempo, mais vidas; empate de vidas é empate.
- Perde vida ao zerar o HP ou sair da blast zone (`ARENA.blast`: `l -150`, `r W+150`, `t -270`, `b H+140`). Respawn com HP 100, hover e invulnerabilidade (`inv`). Suicídio não dá crédito de KO.
- Mapa **Ilhas do Céu** (`ARENA.surf`): chão `x 172–622, y 296`, e duas plataformas macias `y 153` (`x 192–336` e `472–612`). ↓ atravessa a macia.
- Sprites a `ARK = 0.27`. Andar `SPD = 3.2` (0,8× para trás). Pulo `vy = -10`, pulo duplo `-9.6` (um só), gravidade `0.5`, queda máx. `12`. Sem air dodge nem wall jump.
- **Knockback** (`AF.hurt`): `lost = 1 - hp/100`; `base = 7` na esfera e `a.kb` nos demais; `kx = face * base * (0.55 + lost * 0.85)`. Pop vertical `base * 0.16 + lost * base * 0.5`, só se passar de 2,6, teto 13. Atrito do deslize: `0.82` no chão, `0.93` atordoado, `0.88` no ar. Dano baixo escorrega; o kill vem perto do fim da vida.
- Medido (chute de P1 em P2 parado no chão, HP antes do golpe 100 / 70 / 40 / 15): `kx` 5,2 / 7,2 / 9,2 / 10,9 e `vy` 0 / −2,9 / −4,1 / −5,1. Receita em `quinhas-qa`.
- Dica de design: a ilha principal tem ~450 px. Mudou a curva, confira que um chute no meio da vida, do centro da ilha, não mata.
- Entrada: cada teclado (máx. 2) ou controle (até 4) entra apertando um botão. Pelo menos 1 humano, 2+ lutadores. CPU entra/sai com +CPU / −CPU. Celular: escolhe 1–3 inimigos (`#amc`); o resto é CPU.

## IA e dificuldade

- `ai(me, o)` (Versus) e `aiArena(me)` (Arena) decidem um `plan` a cada `pt` quadros e devolvem o mesmo formato do jogador `{l,r,u,d,p,k,h,b}`.
- `DIFF` (`e` Fácil, `n` Normal, `h` Difícil; `qf_diff`) alimenta `aiTune()`:

| Nível | `wait` | `brave` | `blk` | `dodge` |
| --- | --- | --- | --- | --- |
| Fácil | 1,85 | 0,34 | 0,012 | 0,02 |
| Normal | 1,2 | 0,62 | 0,04 | 0,045 |
| Difícil | 0,72 | 0,94 | 0,10 | 0,08 |

`wait` multiplica o tempo entre decisões, `brave` é a chance de atacar quando pode, `blk` a de bloquear um golpe vindo, `dodge` a de reagir a projétil. Dificuldade não altera dano nem knockback.
- Hoje o seletor está só em Opções. Estava combinado levá-lo à seleção (Versus: quando o rival é CPU; Arena: um nível para todas as CPUs); ver roadmap.

## Elenco

12 lutadores jogáveis (`ROSTER`/`LAB`, ordem alfabética) + 3 "em breve" (Agui-El, Ale-Xan, Vito-Sama) + Aleatório. Altura real em `HM` define o tamanho; tabela em [visual-identity.md](visual-identity.md).
