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

Menu → **Arena · até 4**. Aperte um botão no teclado (WASD ou setas — máx. 2 teclados) ou em qualquer controle (até 4) para entrar num slot; slots livres podem virar IA. Stock de 3 vidas no mapa **Ilhas do Céu**: perde vida quem zera o HP ou cai fora do mapa. Na Arena ↑ não pula: o pulo é `K` (WASD), `Num 5` (setas) ou ✕/A no controle, e de novo no ar dá pulo duplo; ↓ atravessa as plataformas. A tela Controles tem abas Versus e Arena. Detalhes em [DOCS.md](DOCS.md) §14.1.

## Documentação

Tudo o que importa para entender ou modificar o jogo (arquitetura, roster, combate, input, áudio, tools) está em **[DOCS.md](DOCS.md)**.

## Versão

**v1.4.0** — ver `#tver` / `#ver` em `index.html`.
