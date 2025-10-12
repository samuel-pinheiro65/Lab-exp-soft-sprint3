import requests
import json
import pandas as pd
import time
from datetime import datetime, timezone

# --- CONFIGURAÇÃO ---
# IMPORTANTE: Substitua "seu_token_aqui" pelo seu Token de Acesso Pessoal do GitHub.
# O token precisa ter pelo menos o escopo 'public_repo'.
TOKEN = "xave"

URL = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "User-Agent": "Python Script"
}

# --- FUNÇÕES AUXILIARES ---

def run_query(query, variables={}, max_retries=3):
    """Executa uma query GraphQL com tratamento de erros e retentativas."""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                URL,
                json={'query': query, 'variables': variables},
                headers=HEADERS
            )
            response.raise_for_status() # Lança exceção para status HTTP 4xx/5xx
            data = response.json()
            if "errors" in data:
                print(f"❌ Erro na API GraphQL: {data['errors']}")
                return None
            return data
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Erro de rede (tentativa {attempt + 1}/{max_retries}): {e}")
            time.sleep(5)
    print("❌ Falha ao executar a query após múltiplas tentativas.")
    return None

def parse_datetime(date_str):
    """Converte string de data ISO 8601 para objeto datetime ciente do fuso horário."""
    if not date_str:
        return None
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


# --- FASE 1: BUSCAR REPOSITÓRIOS ELEGÍVEIS ---

def buscar_repositorios_elegiveis(total_repos=200, min_prs=100):
    """Busca os repositórios mais populares e filtra pelos que têm um número mínimo de PRs."""
    print(f"🔎 Iniciando a busca por {total_repos} repositórios com pelo menos {min_prs} PRs (MERGED ou CLOSED)...")
    
    repositorios_elegiveis = []
    cursor = None
    
    query = """
    query buscaRepos($cursor: String) {
      search(query: "stars:>1000 sort:stars-desc", type: REPOSITORY, first: 50, after: $cursor) {
        pageInfo {
          endCursor
          hasNextPage
        }
        edges {
          node {
            ... on Repository {
              owner { login }
              name
              pullRequests(states: [MERGED, CLOSED]) {
                totalCount
              }
            }
          }
        }
      }
    }
    """
    
    while len(repositorios_elegiveis) < total_repos:
        data = run_query(query, {"cursor": cursor})
        
        if not data or not data.get("data", {}).get("search"):
            print("❌ Falha ao buscar repositórios. Interrompendo.")
            break

        search_results = data["data"]["search"]
        
        for edge in search_results["edges"]:
            repo = edge["node"]
            if repo.get("pullRequests", {}).get("totalCount", 0) >= min_prs:
                repositorios_elegiveis.append({
                    "owner": repo["owner"]["login"],
                    "name": repo["name"]
                })
                print(f"  [+] Repositório elegível encontrado: {repo['owner']['login']}/{repo['name']} - PRs: {repo['pullRequests']['totalCount']} ({len(repositorios_elegiveis)}/{total_repos})")
                if len(repositorios_elegiveis) >= total_repos:
                    break
        
        if not search_results["pageInfo"]["hasNextPage"]:
            print("⚠️ Atingido o fim da busca de repositórios antes de encontrar a quantidade desejada.")
            break
            
        cursor = search_results["pageInfo"]["endCursor"]

    print(f"✅ Fase 1 concluída: {len(repositorios_elegiveis)} repositórios elegíveis encontrados.")
    return repositorios_elegiveis


# --- FASE 2: COLETAR DADOS DOS PULL REQUESTS ---

# <<< ALTERAÇÃO 1: Parâmetro renomeado para refletir o limite por repositório >>>
def coletar_dados_pull_requests(repositorios, max_prs_por_repositorio=None):
    """Coleta e filtra Pull Requests dos repositórios fornecidos."""
    print("\n🔎 Iniciando a coleta de dados de Pull Requests...")
    if max_prs_por_repositorio:
        print(f"   -- Limite máximo de {max_prs_por_repositorio} PRs por repositório --")
    
    dados_prs = []

    query_pr = """
    query buscaPRs($owner: String!, $name: String!, $cursor: String) {
      repository(owner: $owner, name: $name) {
        pullRequests(states: [MERGED, CLOSED], first: 25, after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
          pageInfo {
            endCursor
            hasNextPage
          }
          nodes {
            # Feedback Final
            state 
            
            # Tempo de Análise
            createdAt
            closedAt
            mergedAt
            
            # Tamanho
            additions
            deletions
            files(first: 1) { totalCount }

            # Descrição
            bodyText

            # Interações
            participants(first: 1) { totalCount }
            comments(first: 1) { totalCount }
            
            # Número de Revisões (para filtro e RQ)
            reviews(first: 1) { totalCount }
          }
        }
      }
    }
    """

    for i, repo_info in enumerate(repositorios):
        owner, name = repo_info["owner"], repo_info["name"]
        print(f"\n--- Processando Repositório {i + 1}/{len(repositorios)}: {owner}/{name} ---")
        cursor = None
        
        # <<< ALTERAÇÃO 2: Contador de PRs é inicializado aqui, para cada repositório >>>
        prs_coletados_neste_repo = 0
        
        while True:
            variables = {"owner": owner, "name": name, "cursor": cursor}
            data = run_query(query_pr, variables)

            if not data or not data.get("data", {}).get("repository", {}).get("pullRequests"):
                print(f"❌ Não foi possível obter PRs para {owner}/{name}. Pulando.")
                break
                
            prs = data["data"]["repository"]["pullRequests"]
            
            for pr in prs["nodes"]:
                # --- APLICANDO FILTROS DE ELEGIBILIDADE ---
                if pr["reviews"]["totalCount"] < 1:
                    continue

                created_at = parse_datetime(pr["createdAt"])
                final_date = parse_datetime(pr["mergedAt"] or pr["closedAt"])
                
                if not created_at or not final_date:
                    continue
                    
                tempo_analise_delta = final_date - created_at
                if tempo_analise_delta.total_seconds() < 3600:
                    continue
                    
                # --- SE PASSOU NOS FILTROS, EXTRAIR MÉTRICAS ---
                dados_prs.append({
                    "repositorio": f"{owner}/{name}",
                    "status_final": pr["state"],
                    "tempo_analise_horas": round(tempo_analise_delta.total_seconds() / 3600, 2),
                    "tamanho_arquivos": pr["files"]["totalCount"],
                    "tamanho_linhas_adicionadas": pr["additions"],
                    "tamanho_linhas_removidas": pr["deletions"],
                    "descricao_caracteres": len(pr["bodyText"]),
                    "interacoes_participantes": pr["participants"]["totalCount"],
                    "interacoes_comentarios": pr["comments"]["totalCount"],
                    "numero_revisoes": pr["reviews"]["totalCount"]
                })
                
                # <<< ALTERAÇÃO 3: Incrementa o contador específico do repositório >>>
                prs_coletados_neste_repo += 1
                
                # Se o limite para este repositório foi atingido, sai do loop de PRs da página atual
                if max_prs_por_repositorio is not None and prs_coletados_neste_repo >= max_prs_por_repositorio:
                    break

            print(f"  ... PRs elegíveis coletados no total: {len(dados_prs)}")

            # <<< ALTERAÇÃO 4: Verifica se o limite do repositório foi atingido para parar a paginação >>>
            if (max_prs_por_repositorio is not None and prs_coletados_neste_repo >= max_prs_por_repositorio) or not prs["pageInfo"]["hasNextPage"]:
                if max_prs_por_repositorio is not None and prs_coletados_neste_repo >= max_prs_por_repositorio:
                    print(f"  ✨ Limite de {prs_coletados_neste_repo} PRs atingido para este repositório.")
                break # Sai do loop 'while True' e passa para o próximo repositório
            
            cursor = prs["pageInfo"]["endCursor"]

    print(f"\n✅ Fase 2 concluída: Coleta finalizada com {len(dados_prs)} Pull Requests elegíveis no total.")
    return dados_prs

# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    # FASE 1
    repositorios_selecionados = buscar_repositorios_elegiveis(total_repos=200, min_prs=100)
    
    if repositorios_selecionados:
        # FASE 2
        # <<< ALTERAÇÃO 5: Define o limite máximo de PRs a serem coletados de CADA repositório. >>>
        # Altere o número ou defina como None para coletar todos os PRs elegíveis.
        LIMITE_POR_REPOSITORIO = 50 
        dados_finais = coletar_dados_pull_requests(
            repositorios_selecionados, 
            max_prs_por_repositorio=LIMITE_POR_REPOSITORIO
        )
        
        if dados_finais:
            df = pd.DataFrame(dados_finais)
            # Salvando os dados em um arquivo CSV
            nome_arquivo = "dados_pull_requests_analise.csv"
            df.to_csv(nome_arquivo, index=False, encoding="utf-8")
            print(f"\n🎉 Sucesso! Os dados foram salvos em '{nome_arquivo}'. Total de PRs coletados: {len(df)}")
        else:
            print("\n⚠️ Nenhum Pull Request elegível foi encontrado após a filtragem.")
    else:
        print("\n⚠️ Nenhum repositório elegível foi encontrado. O script não pode continuar.")