# rpa-template

Este é um template RPA (Robotic Process Automation) usando python. O template fornece uma estrutura base para implementar automações web com suporte a filas SQS para processamento assíncrono.

## Estrutura do Projeto

```
|___ app.py           # Aplicação FastAPI principal
|
|___ processes/       # Processos de worklow
|
|___ models/          # Modelos de dados
|
|___ libraries/       # Bibliotecas utilitárias
|
|___ infra/           # Configurações de infraestrutura
|
|___ setup/           # Configurações do ambiente
|
|___ page_object/     # Objetos de página (Page Objects)
|
|___ page_handler/    # Manipuladores de página
|
|___ captcha_handler/ # Manipuladores de CAPTCHA
```