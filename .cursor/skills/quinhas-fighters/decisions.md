# Decisões já tomadas

Não reabra isto sem o autor pedir. Código em `index.html` manda se este arquivo envelhecer.

## Telas

- Título: logo, "toque ou qualquer tecla" sobre a foto e sob o logo, legível. Versão no canto, sem cobrir a frase. Sem vídeo de abertura.
- Menu: logo no lugar do título escrito. Fundo da foto preenche a tela (pode cortar a foto). Lutadores não aparecem atrás do menu. Dois modos: **Versus · 1-2** e **Arena · 2-4**, mais Controles, Opções e voltar ao título. Versão no canto.
- Depois da luta: revanche, escolher outros lutadores, controles, opções, menu. Sem pilha de botão.
- Pause durante a luta inclui Controles. No celular deitado, duas colunas, letra legível, sem cortar. O botão de pausar não cobre o retrato do P2.
- Controles: abas Versus e Arena. Sem dica extra embaixo se apertar a tabela. Duas colunas P1/P2; se um controle for usado, as colunas passam a mostrar o pad.
- Opções: sliders de música e efeito, mudo, e dificuldade Fácil / Normal / Difícil (`qf_diff`). Vale para os dois modos. Ainda não há seletor na seleção de personagem.
- Seleção de mapa: tudo na tela, sem scroll. Mapa aleatório tem a arte própria. Templo da Montanha fica oculto até haver um mapa na altura dos outros.
- Nomes estilizados (`assets/names`) na seleção, na mesma proporção. Não vão na barra de vida. No pause, o texto do round continua legível.
- Barra de vida segue o corte diagonal. Sem retângulo preto atrás do nome.

## Versus

- A grade é a de antes. No preview de corpo, "pressione para entrar". Nada começa pré-selecionado: o anel só aparece quando o jogador entra.
- Sozinho, o P1 escolhe o seu e depois o da CPU. O segundo slot mostra **CPU**, não P2.
- Cursores sobrepostos misturam as cores. Confirmar é aro e lavagem de cor, sem check.
- Dica não fica em cima de Voltar. Não repita a mesma dica em cima e embaixo.
- Teclado igual ao de sempre (WASD / setas, J soco, I chute, L esfera, Espaço defesa). No controle: □/X soco, △/Y chute, ○/B esfera, ✕/A pula (o stick também pode), R1/RB defesa, L1/LB especial em breve. Pular no Versus de controle é um **ou** outro, não os dois juntos.
- No celular o preview de corpo some. Sem botão de dois jogadores. Os botões da luta são os mesmos da Arena: soco, chute, esfera, pulo e defesa, cor de PlayStation, ícones brancos sem glow. Analógico para cima **não** pula.

## Arena

- Desktop: quatro vagas, cada controle ou teclado entra com um botão. Máximo dois teclados. Quatro humanos cabem (2 teclados + controles, ou 4 controles). Pelo menos um humano. CPU entra e sai com +/−. Começar só com humanos confirmados e 2+ lutadores.
- Celular: o lobby antigo. Escolhe a quantidade de inimigos e o personagem. O resto é CPU. Não troque isso pela tela de quatro vagas.
- Mapa Ilhas do Céu, 3 vidas, todos contra todos. Perde vida quem zera o HP ou cai. Último vivo vence. 5:00 acaba em mais vidas, empate é empate.
- Personagem pequeno no mapa. Pulo duplo para chegar na plataforma de cima. Queda não é um tijolo. Sombra é elipse de pé a pé, não uma bola. Pé encosta no chão, embaixo e em cima.
- Ele não vira sozinho para o inimigo. Vira quando o jogador anda para aquele lado.
- Stick para cima não pula. Pulo é ✕/A. No teclado, W e ↑ pulam; de novo no ar é o segundo pulo. ↓ atravessa plataforma. K / Num5 / L1 é especial em breve.
- HUD e timer compactos, timer no meio da rocha se ficar mais limpo.

## Roster

Altura real, no preview e na luta. Trocar de um alto para um baixo não pode piscar scrollbar.

| Lutador | m |
| --- | --- |
| Eslepe, Junin | 1,85 |
| Quinhas, Cai-Ren, Samu, Mestre Leco | 1,75 |
| Luan, Taka | 1,70 |
| Giu, Cris | 1,65 |
| Yas, Bea | 1,60 |

Ordem alfabética. Cards de rosto não se cortam e não ganham silhueta. "Em breve" (Agui-El `#F96B5B`, Ale-Xan `#2C393F`, Vito-Sama `#F2F0F2`) é cadeado; a silhueta preta é só no corpo. Aleatório usa a silhueta preta do Eslepe no corpo e o card `?` que já existe. Não desenhe outro `?`.

Pose nova não reescala as antigas. Quinhas fechado não se recorta de novo. Um frame por pose. Andar é uma pose só, para frente e para trás, flutuando pouco, punho da pose parada, sem saltitar. Parado fica com o pé no chão. Agachar existe. A esfera sai na altura da mão. O nome do golpe é **Esfera de Ki**.

## Combate

- O soco acerta quando o desenho encosta. A esfera acerta mesmo de perto.
- Efeito de luz do soco fica na altura do braço. Mexer no Quinhas parado não desce o soco aéreo, o agachado, nem o dos outros.
- Defesa não treme.
- Ao pousar do pulo, não toca a pose de agachar.
