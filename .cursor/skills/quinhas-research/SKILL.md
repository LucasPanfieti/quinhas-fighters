---
name: quinhas-research
description: Pesquisa técnica e benchmarking para o Quinhas Ball Fighters. Use quando uma decisão depende de documentação oficial (MDN, Gamepad API, Web Audio, Canvas, CSS, Pointer/Touch) ou de como jogos de referência fazem algo (Brawlhalla, Street Fighter, Mortal Kombat, Injustice, Smash), antes de decidir ou implementar.
---

# Pesquisa e benchmarking — Quinhas Ball Fighters

Pesquise **quando a resposta não está no código nem no histórico**. Não pesquise o que `Grep` responde.

## Quando pesquisar

- API do navegador com comportamento sutil: Gamepad (`navigator.getGamepads`, mapeamento `standard`, `buttons[i].pressed`), Web Audio (`AudioContext` e unlock por gesto), Canvas, Fullscreen, `localStorage`, `matchMedia`, `env(safe-area-inset-*)`, `dvh`, `touch-action`, eventos de ponteiro.
- Compatibilidade (Safari iOS, Chrome Android, Firefox) de recurso que o jogo usa ou vai usar.
- Como um jogo de referência resolve algo: seleção e navegação (SF, MK, Injustice), arena e kill por dano (Brawlhalla, Smash), controle em celular, dificuldade de CPU.
- Padrão de acessibilidade ou de interface (alvo de toque, contraste, foco).

## Fontes, em ordem de confiança

1. **Documentação oficial**: MDN Web Docs, especificações W3C/WHATWG, `caniuse.com` para suporte.
2. **Oficial do jogo**: wiki e notas de patch do desenvolvedor (por exemplo Brawlhalla, Street Fighter, Mortal Kombat), guias do estúdio.
3. **Fonte profissional**: GDC (palestras), Game Developer, análises de design de jogos de luta com autoria clara.
4. **Comunidade** (wiki de fãs, fóruns, vídeos): só para fatos de jogo, marcado como menos confiável e sempre com confirmação em outra fonte.

Ferramentas: `WebSearch` e `WebFetch`. Prefira abrir a página da fonte a confiar no resumo do resultado de busca.

## Como pesquisar

1. Escreva a pergunta em uma frase (o que preciso decidir?).
2. Busque a fonte mais alta que existir. Abra a página, não só o trecho.
3. Cheque a data: API de navegador e meta de jogo mudam. Diga a versão ou a data quando importar.
4. Confirme comportamento duvidoso **no próprio jogo** (receitas de `quinhas-qa`), não só na leitura.
5. Adapte ao Quinhas. O jogo é compacto, anime, de navegador: copiar a regra de um jogo grande inteira quase nunca serve.

## O que entregar

Curto, em português:

- **Pergunta** e **resposta** em duas ou três frases.
- **Fontes** com link (markdown) e data de acesso quando relevante.
- **O que se aplica ao Quinhas** e o que não, com o motivo.
- **Recomendação** única, mais a alternativa se houver trade-off real.
- **Incertezas**: o que não deu para confirmar.

Se a pesquisa muda uma decisão do autor (`decisions.md`) ou um número de combate, apresente antes de aplicar.

## Limites

- Não instale pacote nem inclua biblioteca externa por causa da pesquisa. Se a recomendação pedir, pergunte.
- Não copie código sem licença clara. Descreva o conceito e escreva o seu.
- Não invente: sem fonte, diga "não confirmei".
- Pesquisa de combate, controles e menus de jogos de referência já feita está resumida em `docs/mechanics.md` e `docs/controls.md`; releia antes de repetir.
