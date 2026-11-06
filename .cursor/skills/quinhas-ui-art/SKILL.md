---
name: quinhas-ui-art
description: UI/UX e direção de arte para o Quinhas Ball Fighters (jogo de luta 2D anime). Use ao criar ou alterar menus, seleção de personagem, HUD, telas, layout responsivo, controle virtual do celular, dicas de botão, cores, tipografia, sprites, ícones e animação visual.
---

# UI/UX e arte — Quinhas Ball Fighters

Norte: **anime 2D, bonito e compacto**, referência de seleção e menu em Street Fighter, Mortal Kombat e Injustice, e HUD/arena em Brawlhalla. Fatos (cores, fontes, escala) em `docs/visual-identity.md`; input em `docs/controls.md`.

## Princípios

1. **Compacto.** Menos elementos, mais respiro. Se a tela parece cheia, remova. Dica, botão e rótulo só entram se ajudam naquele instante.
2. **Sem corte, sem scroll.** Nada pode cortar nem rolar no celular, em pé ou deitado. Projete para 320 px e para telas baixas (altura < 420).
3. **Um fluxo, três jeitos de jogar.** Teclado/mouse, controle e toque chegam ao mesmo resultado. Foco visível (`.gf`) para quem navega por teclado/pad; alvo de toque ≥ 44 px.
4. **Padrão do gênero.** Seleção: lutadores face a face, grade embaixo, nome em cima, aro no card. Confirmar é aro cheio e cor, não selo, não check.
5. **Consistência.** Versus e Arena usam o mesmo cursor, o mesmo aro, a mesma mistura de cores quando se sobrepõem. O que existe num modo deve parecer o do outro.
6. **Rótulo honesto.** CPU diz **CPU**, não P2. A dica de botão mostra o que o jogador **tem na mão** (teclado, Xbox ou PlayStation).

## Identidade

- Paleta de `:root` (`--ink --dusk --ember --bone --blue --neon --neon2`). Cores de jogador: P1 laranja, P2 azul, P3 verde, P4 rosa. Não introduza cor nova sem motivo; se introduzir, registre em `docs/visual-identity.md`.
- Dela Gothic One para logo e títulos; Rajdhani para o resto. Botão de menu itálico com `skewX(-6deg)`.
- Fundo de menu: foto do cenário, preenchendo a tela, sem logo e sem lutadores atrás.
- Ícone de controle: o padrão do gamepad em uso. Navegar é setas (D-pad), não analógico.

## Sprites e arte

- Uma pose por imagem, fundo transparente, borda limpa. Proporção do personagem pela altura real (`HM`).
- Pose nova **não** reescala as antigas. Mostre antes e depois.
- Detalhes de acabamento já decididos: pé no chão, sombra em elipse de pé a pé, defesa sem tremer, efeito de luz do soco na altura do braço.
- Ao pedir arte ao autor, gere prompts curtos em português, uma pose por imagem.

## Como entregar uma mudança de UI

1. Veja a tela **antes** (screenshot ou medida).
2. Faça a mudança e confira no desktop largo, desktop baixo, celular em pé e celular deitado (`?touch=1` ou emulação).
3. Percorra o fluxo pelos três jeitos de jogar (veja `quinhas-qa`).
4. Procure sobreposição (dica sobre botão, HUD sobre sprite), corte e scroll com `getBoundingClientRect` em vez de confiar no olho.
5. Atualize `docs/visual-identity.md` se mudou cor, fonte ou componente.

## Armadilhas já vistas

- Regra de lift para dica dentro de `@media (min-width:…)`: sumiu no resto.
- `outline` em painel `height:100%` virou barra laranja de tela inteira.
- Prévia de corpo de altura variável faz a barra de rolagem piscar ao trocar de alto para baixo.
- Dica de teclado escondida em tela baixa e escondida de novo no toque: o jogador ficou sem dica nenhuma.
- Emulação de dispositivo (Device Metrics) não muda a altura do `#stage`; meça a altura real.
