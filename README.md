<h2 align="center">Trabalho 1 - Controle de Cruzamentos de Trânsito com Câmeras LPR</h2>
<br>

## Sumário
- [Visão geral](#visão-geral)
- [Como executar o projeto](#como-executar-o-projeto)
- [Desenvolvedoras](#desenvolvedoras)

## Visão geral
O projeto consiste no desenvolvimento de um sistema distribuído na Raspberry Pi para controlar e monitorar cruzamentos de trânsito, utilizando GPIO para interação com sinais e sensores, e comunicação UART/RS485 para integração com o simulador.

A proposta completa do projeto pode ser consultada [aqui](https://gitlab.com/fse_fga/trabalhos-2026_1/trabalho-1-2026-1/-/tree/main?ref_type=heads).

## Como executar o projeto

### Pré-requisitos

Antes de começar, certifique-se de ter:

- Uma Raspberry Pi com o sistema operacional instalado e acesso aos pinos GPIO;
- Git instalado.

Após isso, com acesso à Raspberry Pi, clone este repositório, acesse a pasta do projeto e siga as instruções abaixo para configurar e executar o projeto.

#### 1) Instale as dependências do sistema:

```
sudo apt-get update
sudo apt-get install python3-pip python3-dev
```

#### 2) Instale a biblioteca RPi.GPIO:

```
pip install -r requirements.txt
```

### Execução

Para iniciar, execute:

```
python3 main.py
```

### Testes

- **Logs:** O programa exibirá no terminal as mudanças de estado dos semáforos e a detecção do acionamento do botão de pedestre.
- **Controle:** Utilize o Dashboard (conforme a figura 1 do enunciado do trabalho - Entrega 1) para interagir com o sistema.

## Desenvolvedoras
<div align="center">
  <table>
    <tr>
     <td align="center">
        <a href="https://github.com/libruna">
          <img src="https://avatars.githubusercontent.com/u/83987201?v=4" width="100px;" alt="Bruna Lima"/><br>
          <sub><b>Bruna Lima</b></sub>
        </a>
      </td>
      <td align="center">
        <a href="https://github.com/Laisczt">
          <img src="https://avatars.githubusercontent.com/u/92321749?v=4" width="100px;" alt=""/><br>
          <sub><b>Laís Soares</b></sub>
        </a>
      </td>
    </tr>
  </table>
</div>