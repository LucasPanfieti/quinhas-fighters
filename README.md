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

## Documentação

Tudo o que importa para entender ou modificar o jogo (arquitetura, roster, combate, input, áudio, tools) está em **[DOCS.md](DOCS.md)**.

## Versão

**v1.3.8** — ver `#tver` / `#ver` em `index.html`.
