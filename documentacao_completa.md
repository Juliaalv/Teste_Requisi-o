# 📊 Documentação Completa do Dashboard de Análise de Chamados

## Índice
1. [O que é este projeto?](#o-que-é-este-projeto)
2. [Como funciona em termos simples](#como-funciona-em-termos-simples)
3. [Os arquivos que compõem o projeto](#os-arquivos-que-compõem-o-projeto)
4. [Como usar o sistema](#como-usar-o-sistema)
5. [Explicação detalhada de cada parte](#explicação-detalhada-de-cada-parte)
6. [Guia de instalação](#guia-de-instalação)

---

## O que é este projeto?

Este é um **Dashboard de Análise de Chamados** desenvolvido para a empresa **Grupo Energisa**. É uma ferramenta que ajuda a equipe a visualizar, organizar e analisar todos os pedidos de serviço (chamados/requisições) de forma clara e intuitiva.

### Objetivo principal
Facilitar o acompanhamento do trabalho realizado pela equipe, mostrando:
- Quais chamados chegaram essa semana
- O status de cada chamado (resolvido, pendente, em andamento, etc.)
- Quem está responsável por cada um
- Se os prazos estão sendo respeitados (análise de SLA)
- Gráficos e análises para entender melhor o volume de trabalho

---

## Como funciona em termos simples

### A Ideia Central

Imagine que você tem **dois arquivos Excel** com informações sobre chamados (pedidos de atendimento):
- **Arquivo 1**: Uma lista grande com TODOS os chamados da empresa
- **Arquivo 2**: Uma lista específica dos chamados da MINHA EQUIPE

O sistema faz o seguinte:

1. **Lê os dois arquivos** Excel quando você faz upload
2. **Mescla as informações** - se um chamado aparece nos dois arquivos, ele usa a informação mais completa/recente
3. **Organiza tudo** - separa por semana, responsável, status, etc.
4. **Salva em um arquivo rápido** para não precisar processar tudo novamente
5. **Mostra na tela** em uma visualização bonita e interativa

### O que você vê na tela

A interface tem:
- **Filtros à esquerda** (sidebar) - para escolher semana, responsável, status
- **Visualização Kanban** - cards mostrando os chamados organizados por dia da semana
- **Gráficos e análises** - para entender melhor os dados
- **Tabelas detalhadas** - se você precisar de informações completas

---

## Os arquivos que compõem o projeto

### Estrutura de pastas

```
📁 Projeto
├── 📄 main.py                    # Arquivo principal
├── 📁 config/
│   └── page_config.py           # Configuração visual da página
├── 📁 components/
│   ├── sidebar.py               # Filtros na esquerda
│   ├── kanban.py                # Visualização tipo Kanban
│   ├── analytics.py             # Gráficos e análises
│   └── footer.py                # Rodapé da página
├── 📁 utils/
│   ├── data_loader.py           # Carrega dados salvos
│   ├── data_processor.py        # Processa e organiza dados
│   └── date_logic.py            # Lógica de datas
└── 📄 requirements.txt          # Bibliotecas necessárias
```

### Explicação de cada arquivo

#### **main.py** - O Coração do Sistema
Este é o arquivo principal. Ele:
- Gerencia o fluxo do programa
- Pede para você fazer upload dos arquivos Excel
- Carrega e processa os dados
- Mostra os filtros e as visualizações

**Em termos simples**: É como o maestro de uma orquestra - coordena tudo.

---

#### **page_config.py** - A Aparência
Define como a página fica visualmente:
- Cores
- Tamanhos de texto
- Estilos dos cards
- Animações (como aquela vibração de urgência)

**Em termos simples**: É como escolher a decoração de uma casa.

---

#### **sidebar.py** - Os Filtros
Cria a barra lateral esquerda onde você escolhe:
- Qual ano e semana quer analisar
- Qual responsável quer ver (ou "Todos")
- Qual status quer filtrar (Resolvido, Pendente, etc.)
- Buscar um chamado específico pelo número

**Em termos simples**: É como os controles de um videogame - você controla o que vê.

---

#### **kanban.py** - A Visualização em Cards
Mostra os chamados em uma visualização tipo **Kanban** (aquele quadro com post-its):
- Cada dia da semana é uma coluna
- Cada chamado é um card/post-it
- A cor do card indica o status
- Se passar do mouse em um card, aparecem informações

**Lógica importante**:
- Chamados **pendentes** mostram na data planejada (DATA_ALVO)
- Chamados **resolvidos** mostram na data que foram resolvidos (DATA_RESOLUCAO)
- Se um card está vibrando = é urgente (vencimento hoje!)

**Em termos simples**: É como um quadro de tarefas físico, mas digital e automático.

---

#### **analytics.py** - Os Gráficos e Análises
Cria várias abas com análises:

1. **Por Data Alvo** - Gráfico de barras empilhadas
2. **Análise SLA** - Se os prazos estão sendo respeitados
3. **Por Responsável** - Quanto cada pessoa fez
4. **Programados vs Extras** - Previstos vs Realizados
5. **Lista Detalhada** - Tabela com todos os chamados
6. **Resumo Detalhado** - Análise por empresa, status, etc.

**Em termos simples**: São "radiografias" dos dados - você vê tudo de diferentes ângulos.

---

#### **data_loader.py** - Carrega Dados Salvos
Depois que você faz o upload uma vez, os dados são salvos em um arquivo rápido (*.parquet*). 
Este arquivo carrega esses dados na próxima vez que você usa o sistema.

**Em termos simples**: É como guardar um bolo na geladeira - da próxima vez não precisa fazer de novo.

---

#### **data_processor.py** - Processa e Organiza Dados
Pega os dados "crus" dos Excel e:
- Converte datas em formato correto
- Cria categorias de status
- Calcula quais chamados violaram SLA
- Cria campos auxiliares (semana, ano, etc.)
- Define cores para cada status

**Em termos simples**: É como limpar e organizar um armário bagunçado.

---

#### **date_logic.py** - Lógica de Datas
Arquivo pequeno que determina a data de exibição de cada chamado:
- Se não resolvido = mostra na data planejada
- Se resolvido = mostra na data que foi resolvido

**Em termos simples**: Decide em qual dia da semana cada chamado aparece.

---

#### **footer.py** - O Rodapé
Mostra na base da página:
- Logo da empresa
- Nome do desenvolvedor

**Em termos simples**: Como a assinatura no final de um documento.

---

#### **requirements.txt** - As Ferramentas Necessárias
Lista de programas/bibliotecas que o sistema precisa para funcionar:

| Biblioteca | O que faz |
|-----------|-----------|
| **streamlit** | Cria a interface visual e interativa |
| **pandas** | Processa e organiza dados (tipo Excel em código) |
| **plotly** | Cria gráficos bonitos e interativos |
| **numpy** | Faz contas matemáticas complexas |
| **openpyxl** | Lê arquivos Excel |
| **pyarrow** | Salva/carrega dados de forma rápida |

---

## Como usar o sistema

### Passo 1: Preparar os Arquivos Excel

Você precisa de **dois arquivos Excel**:

#### Arquivo 1: Relatório de Requisições.xlsx
Deve conter colunas como:
- NUM_CHAMADO (número do chamado)
- DATA_ABERTURA (quando foi criado)
- DATA_PREV_SOLUCAO (previsão de quando resolver)
- DATA_RESOLUCAO (quando foi resolvido)
- Status (situação atual)
- RESPONSAVEL (quem está trabalhando nisso)
- TITULO (resumo do problema)
- SOLICITANTE (quem pediu)
- Etc.

#### Arquivo 2: Requisições da Minha Equipe.xlsx
Deve conter colunas como:
- Requisição de Serviço (número do chamado)
- Data Esperada (previsão)
- Status (situação)
- Proprietário (responsável)
- Criado em (data de criação)
- Resolvido em (data de resolução)
- Etc.

### Passo 2: Fazer Upload dos Arquivos
1. Abra o sistema
2. Verá uma tela pedindo para fazer upload
3. Selecione o Arquivo 1
4. Selecione o Arquivo 2
5. Clique em "🚀 Processar Dados e Iniciar Análise"

### Passo 3: Usar os Filtros
Na esquerda (sidebar), escolha:
- **Ano**: Qual ano quer ver
- **Semana**: Qual semana do ano (1-52)
- **Responsável**: Selecione uma pessoa ou "Todos"
- **Status**: Escolha qual/quais status quer ver
- **Buscar**: Digite o número de um chamado para ver detalhes

### Passo 4: Interpretar as Visualizações

#### Visualização Kanban (padrão)
- Mostra 7 colunas (segunda a domingo)
- Cada card é um chamado
- Cores indicam status:
  - 🟢 Verde = Resolvido
  - 🔵 Azul = Em Andamento
  - 🟡 Amarelo = Pendente
  - 🔴 Vermelho = Cancelado
  - Vibração = URGENTE (vence hoje)

#### Abas de Análise (Analytics)
Clicar nas abas para ver:
- Gráficos de volume
- Análise de SLA (prazos)
- Quantos cada responsável fez
- Taxas de conclusão
- Listas completas com detalhes

---

## Explicação detalhada de cada parte

### 1. O Processo de Upload e Merge de Dados

Quando você faz upload dos dois arquivos, o sistema:

```
Arquivo 1 (Grande)     Arquivo 2 (Equipe)
+                      +
|                      |
v                      v
┌──────────────────────────────┐
│  Ler ambos os Excel files    │
└──────────────────────────────┘
            │
            v
┌──────────────────────────────────────┐
│  Renomear colunas para ficar igual   │
│  (NUM_CHAMADO, STATUS, etc.)         │
└──────────────────────────────────────┘
            │
            v
┌──────────────────────────────────────┐
│  MERGE (mesclar) pelo número chamado │
└──────────────────────────────────────┘
            │
            v
┌──────────────────────────────────────┐
│  Prioridade: dados do Arquivo 2      │
│  (porque é mais específico)          │
└──────────────────────────────────────┘
            │
            v
┌──────────────────────────────────────┐
│  Salvar em arquivo rápido (.parquet) │
└──────────────────────────────────────┘
```

### 2. O Cálculo da DATA_ALVO (Data Planejada)

O sistema tenta, **em ordem de prioridade**:

1. Usar **Data Esperada** (Arquivo 2)
2. Se não houver → usar **DATA_QUEBRA_SLA**
3. Se não houver → usar **DATA_PREV_SOLUCAO**
4. Se nada disso existir → descarta o chamado

Esta data é importante porque define em qual dia da semana o chamado aparece no Kanban.

### 3. Cálculo do SLA (Cumprimento de Prazos)

```
Se DATA_RESOLUCAO existe E Status é "Resolvido" ou "Fechado":
   Se DATA_RESOLUCAO > DATA_PREV_SOLUCAO:
      SLA VIOLADO = ❌ (Atrasou)
   Senão:
      SLA OK = ✅ (No prazo ou adiantado)
Senão:
   Não aplicável (ainda aberto)
```

### 4. Animação de Vibração (Cards Urgentes)

Um card vibra quando:
- DATA_ALVO = DATA_PREV_SOLUCAO = HOJE
- Status NÃO É: Resolvido, Fechado ou Cancelado

É como um alarme visual: "Cuidado! Vence hoje e ainda não foi resolvido!"

### 5. Como Funciona a Visualização Kanban

```
SEGUNDA    TERÇA      QUARTA     QUINTA
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ 2 chamadas│ 1 chamada│ 3 chamadas│ 0 chamadas│
├────────┤ ├────────┤ ├────────┤ ├────────┤
│ #123 ✅ │ │ #456🔵 │ │ #789 ⏳ │ │ Sem    │
│ #124 ⏳ │ │        │ │ #790 ⏳ │ │ chamadas│
└────────┘ └────────┘ │ #791 🟡 │ └────────┘
                      └────────┘
```

Se clicar em "Veja +", mostra todos.

### 6. Métricas Mostradas

Na sessão de métricas, você vê:

- **📋 Total**: Quantos chamados nesta semana
- **✅ Resolvidos**: Quantos foram resolvidos
- **⏳ Em Aberto**: Quantos ainda estão pendentes
- **🚨 SLA Violado**: Quantos extrapolaram o prazo
- **🎯 Taxa SLA**: Percentual de chamados dentro do prazo

### 7. Os Gráficos

#### Gráfico de Barras Empilhadas
Mostra por dia e por status quantos chamados há.

#### Gráfico Pizza
Distribuição percentual de status.

#### Tabelas
Números exatos para você consultar.

---

## Guia de instalação

### Requisitos Básicos
- Python 3.8 ou superior
- Pip (gerenciador de pacotes do Python)
- Dois arquivos Excel com dados de chamados

### Passo 1: Preparar o Ambiente

Abra o terminal/prompt e navegue até a pasta do projeto:

```bash
cd caminho/para/pasta/do/projeto
```

### Passo 2: Instalar as Bibliotecas

Execute:

```bash
pip install -r requirements.txt
```

Isso instalará todas as ferramentas necessárias.

### Passo 3: Colocar a Imagem da Logo (Opcional)

Coloque um arquivo chamado `Grupo.svg.png` na pasta do projeto, para aparecer no rodapé. Se não tiver, o sistema funciona normalmente sem a imagem.

### Passo 4: Executar o Sistema

```bash
streamlit run main.py
```

Seu navegador abrirá automaticamente com o dashboard.

### Passo 5: Fazer Upload dos Arquivos

Quando aparecer a tela, siga as instruções para fazer upload dos arquivos Excel.

---

## Dicas e Boas Práticas

### ✅ Faça assim:
- Mantenha os nomes das colunas nos Excel consistentes
- Coloque datas em formato claro (DD/MM/YYYY ou YYYY-MM-DD)
- Use um número único para cada chamado
- Atualize os arquivos regularmente

### ❌ Evite:
- Deixar células vazias em colunas importantes
- Usar datas em formatos estranhos
- Duplicar números de chamados
- Ter colunas com nomes muito diferentes nos dois arquivos

---

## Troubleshooting (Solução de Problemas)

### ❌ "Arquivo de dados não encontrado"
**Solução**: Faça upload dos dois arquivos Excel e clique em "Processar Dados"

### ❌ "Nenhuma coluna de data alvo encontrada"
**Solução**: Verifique se seus Excel têm as colunas de data (DATA_ALVO, DATA_PREV_SOLUCAO, etc.)

### ❌ "Nenhum dado válido encontrado"
**Solução**: Verifique se há datas válidas nas colunas de data

### ❌ O sistema está lento
**Solução**: Isso é normal com muitos dados. Tente filtrar por responsável ou status específico.

### ❌ Os números não fazem sentido
**Solução**: Verifique se as datas nos seus Excel estão corretas

---

## Resumo Visual

```
┌─────────────────────────────────────────────────────┐
│         SISTEMA DE ANÁLISE DE CHAMADOS             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ENTRADA:          PROCESSAMENTO:      SAÍDA:     │
│  ┌──────────┐     ┌──────────────┐     ┌────────┐ │
│  │Excel 1   │────▶│Merge de dados│────▶│Kanban  │ │
│  │          │     │Organizar por:│     │        │ │
│  └──────────┘     │- Semana      │     │Gráficos│ │
│  ┌──────────┐     │- Status      │     │        │ │
│  │Excel 2   │────▶│- Responsável │────▶│Análises│ │
│  │          │     │Calcular SLA  │     │        │ │
│  └──────────┘     │Encontrar     │     │Filtros │ │
│                   │urgentes      │     │        │ │
│                   └──────────────┘     └────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Conclusão

Este sistema foi desenvolvido para **simplificar e agilizar** o acompanhamento de chamados da equipe de telecom do Grupo Energisa. 

Com ele, é possível:
- ✅ Visualizar chamados de forma clara e organizada
- ✅ Identificar urgências rapidamente
- ✅ Acompanhar prazos (SLA)
- ✅ Analisar tendências e padrões
- ✅ Melhorar a comunicação da equipe

Se tiver dúvidas ou sugestões, converse com a equipe de desenvolvimento!

---

**Desenvolvido por: Júlia Alves Santos | GEAT - Grupo Energisa**
**Data: 2025**