# Roadmap

Só o que **ainda não existe**. Nada daqui está no código; não documente como pronto em `mechanics.md`.

## Modo Arcade (planejado)

Não há uma linha dele em `index.html`: nenhuma tela, estado ou função `arcade`. O menu tem só Versus e Arena.

Antes de desenhar, o autor deve definir (perguntar, não inventar):

- Formato (escada de lutas contra a CPU, chefe final, continues?).
- Quantas lutas e como escolhem o rival (ordem fixa, aleatória, por personagem).
- Se há história/final por personagem ou só placar.
- Se joga 1 ou 2 jogadores em cooperativo.

Pontos do código que o modo vai tocar:

- **Menu**: terceiro modo no `#menu` e em `scr()`.
- **Luta**: reaproveitar `begin`/`beginNow`/`startRound` (Versus) com `mode = "ai"` e uma sequência de rivais; ao fim do match, em vez do menu pós-partida, avançar para a próxima luta.
- **IA**: escala por luta via `aiTune()`/`DIFF`.
- **Estado**: `LASTM` já guarda a última luta; uma campanha precisa de estado próprio (fase, vidas/continues, rivais já enfrentados).
- **Persistência**: se salvar progresso, chave nova em `localStorage` (padrão `qf_*`).

## Combinados e ainda não feitos

- **Dificuldade dentro de cada modo**: hoje só em Opções. Combinado: Versus mostra o nível quando o rival é CPU; Arena tem um nível único para as CPUs da partida. Um nível por vaga não entra.
- **Especial** (K / Num 5 / L1·LB): botão existe, sem efeito.
- **Três lutadores "em breve"**: Agui-El, Ale-Xan, Vito-Sama (cards e cores já existem; faltam sprites).
- **Mapa Templo da Montanha**: existe e está oculto; só volta com altura compatível com os outros.
- **Multiplayer online**: levantado como ideia distante; não há plano nem código.
