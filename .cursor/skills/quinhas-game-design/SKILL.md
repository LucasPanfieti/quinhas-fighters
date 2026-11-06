---
name: quinhas-game-design
description: Game design de jogo de luta 2D para o Quinhas Ball Fighters. Use ao ajustar golpes, dano, alcance, knockback, hitstop, IA e dificuldade, equilíbrio, ritmo da partida, regras do Versus e da Arena, ou ao projetar o modo Arcade.
---

# Game design — Quinhas Ball Fighters

Dois jogos em um. **Não misture as referências.** Fatos e números em `docs/mechanics.md`; planos em `docs/roadmap.md`.

## Versus — Street Fighter, Mortal Kombat, Injustice

- Luta no chão, melhor de 3, paredes no palco, sem blast zone.
- O golpe tem que ser legível: startup, ativo e recuperação (`ATK.s/a/n`). Golpe rápido causa pouco; golpe lento causa muito e é punível.
- Acertar é o desenho encostar. Hitbox que não bate com o sprite é bug de design, não "balanceamento".
- Defesa existe e custa: bloqueio tira 15% do dano, mas não faz o lutador invencível.
- O empurrão deixa os dois no alcance para a troca seguinte. Empurrão grande demais mata o ritmo.
- Pressão e punição: CPU que bloqueia tudo ou ataca sem parar não é divertida.

## Arena — Brawlhalla

- Estoque (3 vidas), plataformas, blast zone, até 4 jogadores.
- **Knockback cresce com o HP perdido** (`AF.hurt`). Com vida cheia o golpe só escorrega; o kill vem no fim da vida. Esse é o contrato do modo.
- Verificação obrigatória ao mexer na curva: da posição central da ilha (~450 px), um chute com vida média não pode tirar da ilha. Meça com os números reais, não no olho.
- Recuperação: pulo + um pulo duplo, ↓ atravessa plataforma macia. Sem air dodge, sem wall jump. Qualquer mecânica nova de recuperação muda o equilíbrio do kill: avise.
- Todos contra todos, fogo amigo sempre ligado.

## Dificuldade da CPU

- Fácil / Normal / Difícil (`DIFF`, `aiTune`). Mexe em reação, coragem e bloqueio, **nunca** em dano ou knockback (o jogador precisa sentir a mesma luta).
- Fácil deve dar para vencer sem conhecer o jogo. Difícil deve punir erro, não ser injusto.
- Uma mudança de IA vale para Versus (`ai`) e Arena (`aiArena`); teste os dois.
- Plano combinado: seletor dentro da seleção de cada modo (Versus quando o rival é CPU; Arena um único nível para todas as CPUs). Um nível por vaga não.

## Como avaliar uma mudança de equilíbrio

1. Diga o que quer sentir ("o jogador vence a CPU normal com ~60% das lutas").
2. Escreva os números antes e depois (`ATK`, `base`, `scale`, `aiTune`).
3. Rode cenários no browser: jogador contra CPU em cada nível; para knockback, force HP e hit (`Runtime.evaluate`) e meça `kx`, `vy` e onde cai.
4. Teste os três jeitos de jogar (teclado, controle, toque) quando a mudança afeta input.
5. Registre o que decidiu em `docs/mechanics.md`.

## Projetar o modo Arcade

Não existe no código. Antes de implementar, leia `docs/roadmap.md`, **pergunte** ao autor formato, número de lutas e escolha de rival, e proponha o plano. Reaproveite `begin`/`startRound` e `aiTune`; não invente um segundo motor de luta.

## Pesquisa

Para como um jogo de referência faz algo (Brawlhalla: dano/knockback, recuperação; SF/MK/Injustice: seleção, ritmo), siga `quinhas-research`: fonte oficial ou profissional, citada, e adapte ao tamanho do jogo (compacto, anime, sem inflar).
