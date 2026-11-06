# Controles

Mapeamento real do código (`KB`, `gin`, `devIn`, `in1`/`in2`, `press`). A tela **Controles** (`#hp`, abas Versus e Arena) mostra isto e troca para os ícones do controle quando um pad é usado.

## Luta

| Ação | Teclado P1 | Teclado P2 | Controle |
| --- | --- | --- | --- |
| Mover | A D | ◀ ▶ | D-pad ou stick |
| Pular | W | ▲ | ✕/A (Versus: também stick ↑ ou D-pad ↑) |
| Agachar / descer | S | ▼ | D-pad ↓ ou stick ↓ |
| Soco | J | Num 4 | □ / X |
| Chute | I | Num 8 | △ / Y |
| Esfera de Ki | L | Num 6 | ○ / B |
| Defesa | Espaço | Num 0 | R1 / RB |
| Especial | K | Num 5 | L1 / LB |
| Pausar | Esc ou P | Esc ou P | Start |
| Mudo | M | M | — |

- **Especial é "em breve"**: a tecla e o botão existem na UI, sem efeito de luta.
- **Versus**: o pulo do controle é um **ou** outro (stick/D-pad ↑ ou ✕/A). **Arena**: stick ↑ **não** pula, só ✕/A. No teclado, W e ▲ pulam nos dois modos; no ar, o segundo toque é o pulo duplo (só Arena).
- Índices do pad (`gin`): D-pad 12–15, eixos 0/1 (zona morta 0,4 e 0,55), soco 2, chute 3, esfera 1, defesa 5, especial 4, confirmar 0, voltar 1, start 9.
- Ícones do controle seguem `padKind`: DualShock/DualSense/etc. mostram □ △ ○ ✕; o resto mostra Xbox. Com um pad ativo, a UI mostra o pad; com teclado, mostra teclas.

## Celular (`#pad`)

Só aparece em luta. Analógico à esquerda; botões à direita no padrão de controle de videogame.

- Botões (`data-k`): `vP` soco, `vK` chute, `vH` esfera, `vJ` pulo, `vB` defesa. Ícones brancos sem glow em `assets/ui/`. O anel de cada botão segue a cor PlayStation (soco rosa, chute verde, esfera vermelho, pulo azul, defesa laranja).
- **O analógico para cima não pula**: pulo só no botão `vJ`.
- Versus no celular usa os mesmos cinco botões da Arena. O botão "especial" é inerte.
- Sem scroll, sem corte, em pé e deitado. Dicas de teclado (`#prompts`) ficam ocultas no toque.

## Menus

Regras valem para teclado, mouse, toque e controle.

| Ação | Teclado | Controle |
| --- | --- | --- |
| Navegar | setas ou WASD | D-pad |
| Confirmar | Enter | ✕/A |
| Voltar (um passo) | Esc | ○/B |
| Sortear (Versus) / +CPU (Arena) | I (Num 8) | △/Y |
| −CPU (Arena) | L (Num 6) | □/X |
| Começar | Enter ou botão | Start |

- `uiBack`/`selStackBack` desfazem **um** passo por vez: confirmação → sair da vaga → tela anterior → menu. Nunca encadeiam até o título.
- A em **Voltar** sai da tela (na Arena, `a4Leave`).
- Setas navegam a grade de verdade (↓ desce, não vai para o lado). A dica de "Navegar" mostra só setas, sem ícone de analógico.
- Cada dispositivo é dono do próprio cursor: na Arena, `a4Focus.dev` impede que o foco do party/ações de um humano mova o dos outros.
- Dois controles no Versus solo não viram P2. CPU é `s2.vs && !s2.hum[1]`.

## Dispositivos na seleção

- **Versus**: o P1 é quem entrar primeiro (`vsIn`). Dispositivos em `VDEV`, lidos por `in1`/`in2`.
- **Arena**: `k1` (WASD/J/I/L/Espaço), `k2` (setas/Numpad), `p0..p3` (controles pelo índice cru de `navigator.getGamepads`). Máx. 2 teclados e 4 controles, pelo menos 1 humano.
- Pad desconectado: mantém a vaga se já confirmou; senão libera.
