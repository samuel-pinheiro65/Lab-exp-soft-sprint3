# Projeto: Coleta e Análise de Repositórios Populares do GitHub (GraphQL API)

Este projeto utiliza a **API GraphQL do GitHub** para coletar informações sobre os repositórios mais populares, armazenando os dados em um arquivo `ados_pull_requests_analise.csv` e permitindo análises através de gráficos.

---

## 🔧 Pré-requisitos

Antes de rodar o projeto, você precisa ter:

1. **Python 3.8 ou superior**  
   Baixe em: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
   Durante a instalação, marque a opção **"Add Python to PATH"**.

2. **Conta no GitHub** e **Token de acesso pessoal** (Personal Access Token).  
   - Crie em: [https://github.com/settings/tokens](https://github.com/settings/tokens)  
   - Dê permissões de leitura para *public_repo*.  
   - Copie e substitua no código na variável `TOKEN`.

3. **Bibliotecas necessárias** instaladas:
   ```bash
   pip install requests pandas python-dateutil

## 🚀 Como executar

### 1. Coletar os repositórios

Execute o script de coleta para buscar os repositórios mais populares e salvar em CSV:

```
python lab03_sprint1.py
```

Isso vai gerar o arquivo:

ados_pull_requests_analise.csv → Contém os dados coletados






