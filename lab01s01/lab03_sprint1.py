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
                print(f"  [+] Repositório elegível encontrado: {repo['owner']['login']}/{repo['name']} ({len(repositorios_elegiveis)}/{total_repos})")
                if len(repositorios_elegiveis) >= total_repos:
                    break
        
        if not search_results["pageInfo"]["hasNextPage"]:
            print("⚠️ Atingido o fim da busca de repositórios antes de encontrar a quantidade desejada.")
            break
            
        cursor = search_results["pageInfo"]["endCursor"]

    print(f"✅ Fase 1 concluída: {len(repositorios_elegiveis)} repositórios elegíveis encontrados.")
    return repositorios_elegiveis


# --- FASE 2: COLETAR DADOS DOS PULL REQUESTS ---

def coletar_dados_pull_requests(repositorios):
    """Coleta e filtra Pull Requests dos repositórios fornecidos."""
    print("\n🔎 Iniciando a coleta de dados de Pull Requests...")
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
            files(first: 1) { totalCount } # Otimização para pegar apenas a contagem

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
        
        while True:
            variables = {"owner": owner, "name": name, "cursor": cursor}
            data = run_query(query_pr, variables)

            if not data or not data.get("data", {}).get("repository", {}).get("pullRequests"):
                print(f"❌ Não foi possível obter PRs para {owner}/{name}. Pulando.")
                break
                
            prs = data["data"]["repository"]["pullRequests"]
            
            for pr in prs["nodes"]:
                # --- APLICANDO FILTROS DE ELEGIBILIDADE ---
                
                # 1. Deve ter pelo menos uma revisão
                if pr["reviews"]["totalCount"] < 1:
                    continue

                # 2. Revisão deve ter levado pelo menos uma hora
                created_at = parse_datetime(pr["createdAt"])
                final_date = parse_datetime(pr["mergedAt"] or pr["closedAt"])
                
                if not created_at or not final_date:
                    continue
                    
                tempo_analise_delta = final_date - created_at
                if tempo_analise_delta.total_seconds() < 3600: # 3600 segundos = 1 hora
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
            
            print(f"  ... PRs elegíveis coletados até agora: {len(dados_prs)}")

            if not prs["pageInfo"]["hasNextPage"]:
                break
            cursor = prs["pageInfo"]["endCursor"]

    print(f"\n✅ Fase 2 concluída: Coleta finalizada com {len(dados_prs)} Pull Requests elegíveis.")
    return dados_prs

# --- EXECUÇÃO PRINCIPAL ---

if __name__ == "__main__":
    # FASE 1
    repositorios_selecionados = buscar_repositorios_elegiveis(total_repos=200, min_prs=100)
    
    if repositorios_selecionados:
        # FASE 2
        dados_finais = coletar_dados_pull_requests(repositorios_selecionados)
        
        if dados_finais:
            df = pd.DataFrame(dados_finais)
            # Salvando os dados em um arquivo CSV
            nome_arquivo = "dados_pull_requests_analise.csv"
            df.to_csv(nome_arquivo, index=False, encoding="utf-8")
            print(f"\n🎉 Sucesso! Os dados foram salvos em '{nome_arquivo}'.")
        else:
            print("\n⚠️ Nenhum Pull Request elegível foi encontrado após a filtragem.")
    else:
        print("\n⚠️ Nenhum repositório elegível foi encontrado. O script não pode continuar.")