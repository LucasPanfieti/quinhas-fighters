# Quinhas Ball Fighters

Fighting game 2D no navegador (melhor de 3). Um único `index.html` + pasta `assets/`.

## Como rodar

Sirva a pasta por HTTP (abrir como `file://` pode falhar ao carregar imagens):

```bash
python -m http.server 8080
```

Abra `http://localhost:8080`.

## Controles (resumo)

| | P1 | P2 / Pad |
|--|----|----------|
| Mover | WASD | Setas / stick |
| Soco | J | Num4 / □ |
| Chute | I | Num8 / △ |
| Esfera de Ki | L | Num6 / ○ |
| Defesa | Espaço | Num0 / R1 |
| Pause | Esc / P | Start |

No celular: analógico à esquerda, botões à direita (gire na horizontal).

## Modo Arena (2–4 lutadores)

Menu → **Arena · 2-4 jogadores**. No computador, aperta um botão no teclado (máx. 2) ou no controle (até 4) para entrar num slot; no celular, escolhe quantos inimigos (1–3) e o personagem. Stock de 3 vidas no mapa **Ilhas do Céu**. Pulo no teclado: `W` / ↑ (de novo no ar = pulo duplo). No controle, só ✕/A (stick ↑ não pula). `K` / Num 5 / L1·LB = especial (em breve). ↓ atravessa as plataformas. Detalhes em [DOCS.md](DOCS.md) §14.1.

## Documentação

| Arquivo | Para quê |
| --- | --- |
| [DOCS.md](DOCS.md) | Referência técnica longa |
| [docs/architecture.md](docs/architecture.md) | Estrutura do código |
| [docs/mechanics.md](docs/mechanics.md) | Golpes, Versus, Arena, IA |
| [docs/controls.md](docs/controls.md) | Teclado, controle, celular |
| [docs/visual-identity.md](docs/visual-identity.md) | Cor, fonte, componentes |
| [docs/roadmap.md](docs/roadmap.md) | O que ainda não existe |
| [.cursor/skills/quinhas-fighters/SKILL.md](.cursor/skills/quinhas-fighters/SKILL.md) | Entrada das skills do agente |
| [.cursor/skills/quinhas-fighters/decisions.md](.cursor/skills/quinhas-fighters/decisions.md) | Decisões de design já aprovadas |

## Versão

**v1.5.0** — ver `#tver` / `#ver` em `index.html`.
