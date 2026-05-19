# OpenWork Linux

OpenWork Linux é um MVP para preparar workstations Linux focadas em usuários SAP + Microsoft.

## O que a ferramenta faz

- Detecta o ambiente Linux automaticamente:
  - distribuição e versão
  - família de pacotes (`apt`/`dnf`)
  - ambiente gráfico/desktops comuns
  - presença de `python3`, `pip`, `git`, `sudo`, `appimage`, `dpkg`, `rpm`
  - conexão com internet
- Gera um relatório de prontidão em `openwork/reports/readiness.yml`.
- Carrega módulos e perfis configuráveis a partir de YAML.
- Permite instalar e validar módulos individualmente.
- Permite instalar perfis completos que agrupam vários módulos.
- Registra todas as etapas de execução em logs locais.
- Abre uma interface gráfica em PT-BR com telas de módulos, perfis e logs.

## Funcionalidades atuais

- `openwork/modules/flameshot`: módulo funcional que instala o `flameshot` usando o gerenciador de pacotes nativo.
- `openwork/modules/test_module`: módulo de teste seguro que simula instalação e validação, ideal para verificar o fluxo da interface.
- `openwork/profiles/sap-tecnico.yml`: perfil inicial que reúne módulos úteis para um setup SAP técnico.
- Interface com botão `Configurar` que executa scripts de configuração adicionais quando presentes.

## Requisitos de sistema

Antes de criar o ambiente virtual, instale as dependências do sistema necessárias para clonar o repositório e criar o `venv`.

Para Debian/Ubuntu e derivados:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

Para Fedora/RHEL/CentOS:

```bash
sudo dnf install git python3 python3-venv python3-pip
```

Para outras distribuições, use o gerenciador de pacotes padrão equivalente.

## Requisitos de GUI

A interface gráfica requer um ambiente de exibição válido. Em uma VM sem sessão gráfica, o aplicativo ainda gera o relatório de readiness, mas a GUI não será exibida.

- Use uma VM com desktop instalado (GNOME, KDE, XFCE, etc.)
- Ou use X11/Wayland forwarding se estiver conectado por SSH

## Uso recomendado

1. Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Se você quiser garantir que o GUI tenha sido instalado corretamente:

```bash
pip install PySide6>=6.5
```

3. Execute a aplicação:

```bash
python3 -m openwork.main
```

2. Execute a aplicação:

```bash
python3 -m openwork.main
```

3. Se a distribuição bloquear a instalação direta de pacotes Python por ser gerenciada externamente (PEP 668):

```bash
bash scripts/setup_venv.sh .venv
source .venv/bin/activate
python3 -m openwork.main
```

## Boas práticas antes de publicar

- Mantenha a pasta `.venv/` fora do controle de versão. Este repositório já usa `.gitignore` para isso.
- Teste sempre em uma VM antes de rodar em seu sistema principal, especialmente porque os módulos reais podem executar `sudo` e instalar programas.
- Não inclua credenciais, chaves privadas ou arquivos de configuração sensíveis no repositório público.

## Onde ficam os artefatos

- Logs de execução: `~/.local/state/openwork-linux/logs`
- Relatório de readiness: `openwork/reports/readiness.yml`

## Estrutura principal

- `openwork/`: código principal da aplicação.
- `openwork/modules/`: módulos de instalação com manifests e scripts.
- `openwork/profiles/`: perfis que agrupam módulos.
- `openwork/ui/`: interface gráfica.
- `scripts/`: utilitários de setup.

## Próximos passos

- Expandir módulos para `brave`, `teams_for_linux`, `onlyoffice` e outros aplicativos.
- Implementar handlers de repositório e validações adicionais.
- Adicionar modo dry-run e confirmação de instalação para perfil.

