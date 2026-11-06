---
name: quinhas-engineering
description: Engenharia de software e JavaScript para o Quinhas Ball Fighters (index.html único, sem build). Use ao escrever, corrigir ou revisar código do jogo, estado global, loop, input, menus, performance, ou ao localizar onde uma mudança deve entrar sem criar regressão.
---

# Engenharia — Quinhas Ball Fighters

Leia primeiro `docs/architecture.md`. O jogo é um arquivo, ~7 mil linhas de JS em um `<script>` sem módulos e sem testes automatizados. A segurança vem de ler antes, mudar pouco e testar de verdade.

## Antes de escrever

1. `Grep` pelo símbolo e leia a função **inteira** e quem a chama. Dois chamadores e você mudou a assinatura? Pare e releia os dois.
2. Procure se já existe: dica de botão (`gI`, `buildHints`), voltar (`uiBack`), confirmar (`uiConfirm`), cursor (`a4Focus`), CPU (`s2.hum`). Reusar é mais seguro que reescrever.
3. Decida o menor ponto de entrada. Versus e Arena têm caminhos separados; só `F` é compartilhada. Mudou `F`? Mudou os dois modos.

## Regras de código

- **Ordem importa.** `const`/`let` de topo não existem antes da linha que os declara (TDZ). Código que roda no boot e usa algo declarado depois precisa de guarda (`try/catch` como `hintTick`).
- **Estado em um lugar.** `st`, `mode`, `paused`, `pendMode`, `s2`, `A4`, `a4Focus`, `fighters`. Não duplique estado em variável nova nem em atributo do DOM que ninguém lê.
- **Atributos para estado visual** (`data-*`, classes). CSS reage ao atributo; não escreva estilo inline para estado.
- **Input por um funil.** Menu: `press(k)`. Luta: `in1`/`in2`/`devIn`. Não leia `keys` ou `navigator.getGamepads()` em outro lugar sem motivo.
- **Pad:** índice de botão em `gin`, no padrão já adotado. Não troque o mapa sem pedido.
- **Dispositivo é dono do cursor** na Arena (`a4Focus.dev`): nenhum humano move o foco do outro.
- **Bordas de pad e de lista:** pad que desconecta no meio, lista vazia, `CH[id]` ainda não montado, load de asset que falha (`LOAD.bad`), toque duplo (`beginBusy`).
- **Arrays em loop:** `splice` por índice (`i`), não por `indexOf` que pode ser `-1`.
- **Performance:** o `render()` roda a cada quadro. Nada de alocar objeto grande, consultar o DOM ou recalcular layout dentro dele. Quadro fixo de 60 Hz em `step()`: lógica de jogo não depende de `dt`.
- **Sem dependências, sem módulos, sem build.** Se algo parece pedir isso, pergunte ao autor.
- **Comentário** só para o porquê que o código não diz (regra de jogo, armadilha de navegador). Português.
- **Não limpe o que não é seu.** Código morto ao lado do trecho? Deixe e avise.

## Depois de escrever

```
python .cursor/skills/quinhas-qa/scripts/check_syntax.py
```

Depois rode o jogo e teste o fluxo (skill `quinhas-qa`). Boot quebrado (tela de carregamento eterna) é quase sempre TDZ ou erro de sintaxe.

## Armadilhas já vistas neste projeto

- `selInfo()` antes de `CH` existir quebra o boot.
- Voltar chamando outra função que volta de novo: recursão entre `s2in` e `#back`. Um passo por Back.
- `PJ.splice(indexOf)` com `-1` removeu o projétil errado.
- Estado de "humano entrou" (`s2.hum`) confundido com "dispositivo conectado": pad desconectado virou CPU.
- Regra de CSS dentro de `@media (min-width:…)` que o autor esperava global (a dica sobre o botão Voltar).
- `display:flex` setado por JS vence CSS sem `!important`.

## Revisão

Ao revisar, procure: regressão no outro modo, estado órfão após voltar de tela, pad desconectado, toque, `?v=` de asset não subido, doc desalinhada.
