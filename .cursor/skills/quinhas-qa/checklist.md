# Checklist de QA

Use só as áreas que a mudança alcança, mais **Boot** sempre. Marque o que rodou.

## Boot (sempre)
- [ ] `check_syntax.py` sem erro.
- [ ] A página carrega, `CH.q` existe, `scr()` mostra `menu` depois do título.
- [ ] Sem asset 404 e sem `LOAD.bad`.

## Menu principal
- [ ] Versus, Arena, Controles, Opções e voltar ao título abrem e voltam.
- [ ] Teclado (setas/Enter/Esc), mouse e controle (D-pad/A/B) chegam aos mesmos lugares.
- [ ] Pós-partida: Revanche, escolher outros, Controles, Opções, Menu.

## Versus (seleção)
- [ ] Nada pré-selecionado; o aro só aparece depois de entrar.
- [ ] Sozinho: P1 escolhe, depois o rival aparece como **CPU**. Dois humanos: P1/P2.
- [ ] Cursores sobrepostos misturam a cor. Confirmar é aro e cor, sem check.
- [ ] ↓ desce a grade; Aleatório não trava.
- [ ] Back desfaz um passo por vez, sem chegar ao título de uma vez.
- [ ] Dois controles no solo não viram P2.

## Arena (seleção)
- [ ] Desktop: 4 vagas, cada dispositivo entra e move o próprio cursor.
- [ ] +CPU / −CPU (I/L, △/□, botões da tela). Sozinho já entra uma CPU.
- [ ] A em **Voltar** sai da tela; B volta um passo.
- [ ] Começar só com humanos confirmados e 2+ lutadores.
- [ ] Celular (`?touch=1`): lobby com 1–3 inimigos e grade de personagens, sem a tela de 4 vagas.

## Luta Versus
- [ ] Round inicia, golpes acertam quando o desenho encosta, esfera acerta de perto.
- [ ] Bloqueio, agachar, pulo; pouso não toca pose de agachar.
- [ ] Fim de round e de partida; Revanche mantém os lutadores.
- [ ] CPU nos três níveis de dificuldade se comporta de forma diferente.

## Luta Arena
- [ ] Pulo + pulo duplo; ↓ atravessa plataforma macia.
- [ ] Knockback: vida cheia escorrega, vida baixa lança; chute com vida média do centro da ilha não mata (receita 3).
- [ ] Blast zone tira a vida; respawn; fim por último vivo e por tempo.
- [ ] Pausa por qualquer humano; Controles abre no pause.

## Opções
- [ ] Sliders de música e efeito (mouse e esquerda/direita); mudo.
- [ ] Dificuldade cicla (clique e setas), salva em `qf_diff` e sobrevive a recarregar.

## Dicas e rótulos
- [ ] A dica mostra teclado ou o controle em uso; Xbox e PlayStation trocam sozinhos.
- [ ] "Navegar" é setas, sem ícone de analógico. Sem Y/Enter fixo.
- [ ] Dica nunca sobre o botão Voltar/Começar; sem dica duplicada.

## Celular (`?touch=1` e emulação)
- [ ] Em pé e deitado, em tela baixa: sem scroll, sem corte, botões ≥ 44 px.
- [ ] Controle virtual: 5 botões; analógico para cima **não** pula.
- [ ] Sem prévia de corpo na seleção; sem faixa de dicas de teclado.
- [ ] Pausa deitada em duas colunas, legível.

## Controle (stub ou pad real)
- [ ] Mapa de `gin` (soco 2, chute 3, esfera 1, defesa 5, especial 4, pulo 0/12).
- [ ] Menu: confirmar 0, voltar 1, Start 9.
- [ ] Desconectar um pad no meio não quebra a seleção nem a luta.

## Regressão geral
- [ ] O outro modo (Versus ↔ Arena) continua igual.
- [ ] Sair e voltar de uma tela não deixa estado velho.
- [ ] `DOCS.md` e `docs/` descrevem o que mudou.
