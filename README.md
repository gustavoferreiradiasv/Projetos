# Python Autoclicker

Autoclicker com interface gráfica em `tkinter`, intervalo configurável em segundos e alternância rápida via botão ou atalho global **F6**.

## Funcionalidades
- Interface gráfica simples com indicador visual de status (`PARADO` / `ATIVADO`).
- Configuração de intervalo entre cliques (suporta ponto ou vírgula, com fallback seguro para `0.1s`).
- Atalho global **F6** para ligar/desligar sem precisar focar na janela.
- Fail-safe do `PyAutoGUI` ativo (mova o mouse para o canto superior esquerdo da tela para interromper de emergência).

## Instalação e execução
```bash
pip install -r requirements.txt
python autoclicker.py