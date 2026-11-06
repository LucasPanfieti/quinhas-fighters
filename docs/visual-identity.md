# Identidade visual

O que está no jogo hoje. O norte é **anime 2D, bonito e compacto**: nada sobrando na tela, nada cortado, tudo legível no celular.

## Cor

Variáveis em `:root` de `index.html`:

| Variável | Valor | Uso |
| --- | --- | --- |
| `--ink` | `#0f0d1a` | fundo, texto sobre claro |
| `--dusk` | `#2b1f4a` | roxo escuro de painéis |
| `--ember` | `#e8743b` | laranja de destaque, foco, P1 |
| `--bone` | `#f3e9d2` | texto claro |
| `--blue` | `#3d6bff` | azul de ação |
| `--neon` / `--neon2` | `#2f7bff` / `#6fc2ff` | azul neon dos menus |

**Jogadores** (`A4C` na Arena): P1 `#ff8a3d` laranja, P2 `#38c8ff` azul, P3 `#7be06a` verde, P4 `#ff5fa8` rosa. CPU em cinza `#9aa8c0`.

**Botões do controle virtual** (cor PlayStation no anel): soco/□ rosa `#ff8fe0`, chute/△ verde `#4be0a8`, esfera/○ vermelho `#ff6b7a`, pulo/✕ azul `#7aa7ff`, defesa laranja `#ffb04a`.

Fundo dos menus é a foto do cenário (sem logo e sem lutadores atrás); lutadores só aparecem na luta ou nos previews da seleção.

## Tipografia

- **Dela Gothic One**: logo, títulos de tela, nomes grandes.
- **Rajdhani** 600/700 (`--ui`, fallback Oswald/Arial Narrow): botões, rótulos, HUD, dicas.
- Botões de menu (`.go`): itálico, inclinados `skewX(-6deg)`, `.go.alt` é a variante secundária. Foco por teclado/controle é a classe `.gf` (laranja, brilho).
- Tamanhos por `clamp()`; nada de fonte fixa que estoure em 320 px.

## Componentes de UI

- **Seleção** (`#sel`): grade de cards com rosto, nomes estilizados (`assets/names`) na mesma proporção, preview de corpo grande face a face atrás da grade no desktop largo (≥1000×560); sem preview de corpo no toque.
- **Cursores**: P1 e P2 têm aro próprio (`data-c1`/`data-c2`). Quando se sobrepõem, as cores se misturam. No solo, o segundo mostra **CPU**.
- **Confirmar**: aro cheio + lavagem de cor na base do card. Sem selo, sem check.
- **Em breve**: card com cadeado/grayscale; no preview de corpo, silhueta preta. Aleatório usa o card `?` e a silhueta do Eslepe.
- **HUD**: barra de vida segue o corte diagonal, sem retângulo preto atrás do nome. Na Arena: cards compactos com vidas e HP, timer no centro.
- **Dicas** (`#prompts`): faixa abaixo dos botões Voltar/Começar, nunca sobre eles. Ícones do pad (□ △ ○ ✕ ou Xbox) conforme o controle em uso. Some no toque.
- **Telas**: nada de scroll no celular, em pé ou deitado. `env(safe-area-inset-*)` respeitado. Menu e pausa deitados usam duas colunas.

## Personagens e escala

Altura real (`HM`) define o tamanho no preview e na luta. Escala `P.sc = SC * HM / REF_M`, com `SC = 0.587`.

| ID | Nome | Cor (`col`) | `HM` |
| --- | --- | --- | --- |
| `b` | Bea-Trix | `#e0b45a` | 1,60 |
| `r` | Cai-Ren | `#8a9bb8` | 1,75 |
| `c` | Cris-Chan | `#f06ab8` | 1,65 |
| `e` | Eslepe-San | `#d98a3a` | 1,85 |
| `g` | Giu-Lee | `#a15cf0` | 1,65 |
| `k` | Junin-Kai | `#f08a24` | 1,85 |
| `u` | Luan-Zin | `#2fbf5a` | 1,70 |
| `l` | Mestre-Leco | `#e03a3a` | 1,75 |
| `q` | Quinhas-Kun | `#3d6bff` | 1,75 |
| `s` | Samu-Kan | `#e8c84a` | 1,75 |
| `t` | Taka-Shin | `#19c6c0` | 1,70 |
| `y` | Yas-Mine | `#c45a8c` | 1,60 |

Em breve: Agui-El `#F96B5B`, Ale-Xan `#2C393F`, Vito-Sama `#F2F0F2`. Na Arena os sprites desenham a `ARK = 0.27`.

## Sprites e arte

- Uma imagem por pose, fundo transparente, recorte limpo (sem franja verde, sem comer roupa).
- Pose nova segue a proporção do personagem; **não** reescala as antigas.
- Parado com o pé no chão. Andar é uma pose só, flutuando de leve, punho como na pose parada. Defesa não treme. Ao pousar do pulo não toca a pose de agachar.
- Efeito de luz do soco na altura do braço.
- Sombra no chão é uma elipse encostando nos pés, não uma bola.
- Logo, título e favicon: `assets/logo.*`, `assets/title.webp`, `assets/favicon*.png` (o favicon não pode cortar).
- Cenários Versus: Colégio Leila Guedes, Casa do Quinhas, Casa do Junin, Casa da Bea. Arena: Ilhas do Céu (`assets/arena.webp`). Personagens ficam um pouco abaixo da quina da calçada.

## Estados e movimento

- Transições de tela suaves. `prefers-reduced-motion` é respeitado no CSS.
- Hitstop de 3 quadros e tremor de tela no acerto; KO do Versus com slow-motion.
- Nada começa pré-selecionado: o anel só aparece depois que o jogador entra.
