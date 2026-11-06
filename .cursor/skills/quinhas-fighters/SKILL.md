---
name: quinhas-fighters
description: Ponto de entrada do projeto Quinhas Ball Fighters (jogo de luta 2D anime em index.html). Use no início de qualquer tarefa do jogo para escolher a skill especializada e aplicar o fluxo analisar, planejar, implementar, testar e validar. Versus segue Street Fighter, Mortal Kombat e Injustice; Arena segue Brawlhalla.
---

# Quinhas Ball Fighters — ponto de entrada

Jogo de luta 2D de navegador: `index.html` (CSS, HTML e JS puros) + `assets/`. Sem build. UI em português. Versus (1–2) e Arena (2–4); Arcade é só plano.

Regras permanentes estão em `.cursor/rules/`. Esta skill diz **qual skill usar** e onde estão os fatos.

## Qual skill usar

| Tarefa | Skill |
| --- | --- |
| Escrever ou corrigir código, estado, input, performance | `quinhas-engineering` |
| Golpes, knockback, IA, dificuldade, ritmo, modo novo (Arcade) | `quinhas-game-design` |
| Telas, menus, select, HUD, celular, sprites, cor, tipografia | `quinhas-ui-art` |
| Testar, caçar bug, verificar visual, evitar regressão | `quinhas-qa` |
| Decidir com base em doc oficial ou jogo de referência | `quinhas-research` |

Tarefa que toca mais de uma: leia todas as relevantes. Quase toda mudança termina em `quinhas-qa`.

## Fatos do projeto

| O que | Onde |
| --- | --- |
| Estrutura e símbolos | `docs/architecture.md` |
| Golpes, Arena, IA, dificuldade | `docs/mechanics.md` |
| Teclado, controle, celular, menus | `docs/controls.md` |
| Cor, fonte, componentes, escala dos personagens | `docs/visual-identity.md` |
| O que ainda não existe (Arcade etc.) | `docs/roadmap.md` |
| Referência técnica longa | `DOCS.md` |
| Decisões já aprovadas pelo autor | [decisions.md](decisions.md) |

O código manda. Doc que discorda do `index.html` está errado: corrija na mesma alteração.

## Protocolo (resumo)

Obrigatório em toda solicitação. Texto completo em `.cursor/rules/workflow.mdc`.

1. **Antes**: entender o pedido, ler o código real e a skill, achar riscos, pesquisar se preciso, planejar a melhor solução.
2. **Durante**: mudança organizada e específica, sem quebrar o que existe, sem solução frágil, na identidade visual, sem deixar pela metade.
3. **Depois**: `check_syntax.py`, jogo rodando no browser, console sem erro, funcionalidades vizinhas, visual em várias resoluções, corrigir e repetir.
4. **Revisão crítica**: fiz o que foi pedido? está profissional? há jeito melhor? quebrei algo? testei os cenários? deixei detalhe passar?
5. **Transparência**: nada de "concluído" sem evidência; diga o que não foi testado.

## Referências por modo

- **Versus**: luta 2D no chão. Seleção face a face, grade embaixo, nome em cima, golpe empurra e não lança para fora.
- **Arena**: Brawlhalla. Estoque, plataformas, blast zone; o kill cresce com o HP perdido.
- **Visual**: anime 2D, compacto, sem enfeite sobrando. Se a tela parece cheia, tire.
- **Navegação**: o mesmo fluxo precisa funcionar no celular, no teclado, no mouse e no controle.
