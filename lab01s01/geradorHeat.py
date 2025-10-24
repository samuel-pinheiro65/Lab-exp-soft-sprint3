# ============================================================
#  Heatmaps para análise de Pull Requests
# ============================================================

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# --- CONFIGURAÇÕES ---
sns.set(style="whitegrid")
plt.rcParams["figure.figsize"] = (10, 7)

# --- CARREGAR CSV ---
df = pd.read_csv("dados_pull_requests_analise.csv")

# --- TRATAMENTO DE DADOS ---
df['num_files'] = pd.to_numeric(df['tamanho_arquivos'], errors='coerce')
df['additions'] = pd.to_numeric(df['tamanho_linhas_adicionadas'], errors='coerce')
df['deletions'] = pd.to_numeric(df['tamanho_linhas_removidas'], errors='coerce')
df['total_lines'] = df['additions'].fillna(0) + df['deletions'].fillna(0)

df['analysis_time_hours'] = pd.to_numeric(df['tempo_analise_horas'], errors='coerce')
df['desc_len'] = pd.to_numeric(df['descricao_caracteres'], errors='coerce')
df['participants_count'] = pd.to_numeric(df['interacoes_participantes'], errors='coerce')
df['comments_count'] = pd.to_numeric(df['interacoes_comentarios'], errors='coerce')
df['num_reviews'] = pd.to_numeric(df['numero_revisoes'], errors='coerce')
df['final_status'] = df['status_final'].astype(str).str.lower()

# --- CRIAR PASTA DE SAÍDA ---
output_dir = Path("graficos_heatmap")
output_dir.mkdir(exist_ok=True)

# ============================================================
# 1️⃣ HEATMAP DE CORRELAÇÃO ENTRE MÉTRICAS NUMÉRICAS
# ============================================================

# selecionar apenas colunas numéricas relevantes
metricas = [
    "num_files",
    "total_lines",
    "analysis_time_hours",
    "desc_len",
    "participants_count",
    "comments_count",
    "num_reviews"
]

corr = df[metricas].corr(method="pearson")

plt.figure(figsize=(9, 7))
sns.heatmap(
    corr,
    annot=True, fmt=".2f",
    cmap="coolwarm", vmin=-1, vmax=1,
    linewidths=0.5, square=True
)
plt.title("Correlação entre Métricas de Pull Requests (Pearson)")
plt.tight_layout()
plt.savefig(output_dir / "heatmap_correlacoes_metricas.png", dpi=200)
plt.close()

print("[✔] Heatmap de correlação salvo como heatmap_correlacoes_metricas.png")

# ============================================================
# 2️⃣ HEATMAP DE MÉDIAS POR STATUS FINAL
# ============================================================

# calcular média das métricas por status_final
status_means = df.groupby("final_status")[metricas].mean().round(2)

plt.figure(figsize=(9, 6))
sns.heatmap(
    status_means,
    annot=True, fmt=".1f",
    cmap="YlGnBu",
    linewidths=0.5
)
plt.title("Médias das Métricas por Feedback Final (Status do PR)")
plt.xlabel("Métricas")
plt.ylabel("Status Final")
plt.tight_layout()
plt.savefig(output_dir / "heatmap_status_final.png", dpi=200)
plt.close()

print("[✔] Heatmap por status_final salvo como heatmap_status_final.png")

# ============================================================
# 3️⃣ HEATMAP DE MÉDIAS POR NÚMERO DE REVISÕES (AGRUPADO)
# ============================================================

# agrupar número de revisões (faixas)
bins = [0, 1, 3, 5, 10, 100]
labels = ["1", "2-3", "4-5", "6-10", "10+"]
df["revisoes_grupo"] = pd.cut(df["num_reviews"], bins=bins, labels=labels, include_lowest=True)

revisoes_means = df.groupby("revisoes_grupo")[metricas].mean().round(2)

plt.figure(figsize=(9, 6))
sns.heatmap(
    revisoes_means,
    annot=True, fmt=".1f",
    cmap="OrRd",
    linewidths=0.5
)
plt.title("Médias das Métricas por Faixa de Nº de Revisões")
plt.xlabel("Métricas")
plt.ylabel("Faixa de Revisões")
plt.tight_layout()
plt.savefig(output_dir / "heatmap_num_revisoes.png", dpi=200)
plt.close()

print("[✔] Heatmap por número de revisões salvo como heatmap_num_revisoes.png")

print(f"\n[✅] Todos os heatmaps salvos em: {output_dir.resolve()}")
