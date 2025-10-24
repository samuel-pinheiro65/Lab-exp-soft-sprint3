# ============================================================
#  Análise de Pull Requests - Gráficos Hexmap com Seaborn
# ============================================================

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import pearsonr, spearmanr

# --- CONFIGURAÇÕES GERAIS ---
sns.set(style="darkgrid")
plt.rcParams["figure.figsize"] = (8, 6)

# --- CARREGAR DATASET ---
df = pd.read_csv(".\dados_pull_requests_analise.csv")

# --- PADRONIZAR NOMES E TIPOS ---
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
df['_status_code'] = pd.Categorical(df['final_status']).codes  # numérico p/ hexbin

# --- CRIAR PASTA DE SAÍDA ---
output_dir = Path("graficos_hexmap")
output_dir.mkdir(exist_ok=True)

# --- FUNÇÃO AUXILIAR PARA PLOT ---
def plot_hex(x, y, xlabel, ylabel, titulo, nome_arquivo):
    # remover NaN
    mask = df[x].notna() & df[y].notna()
    xdata, ydata = df.loc[mask, x], df.loc[mask, y]

    if len(xdata) < 10:
        print(f"[!] Poucos dados para {titulo}")
        return

    # calcular correlações
    pear, _ = pearsonr(xdata, ydata)
    spear, _ = spearmanr(xdata, ydata)

    # plot seaborn
    g = sns.jointplot(
        data=df, x=x, y=y, kind="hex", color="royalblue",
        gridsize=35, marginal_ticks=True
    )

    g.set_axis_labels(xlabel, ylabel)
    plt.suptitle(f"{titulo}\nPearson={pear:.2f} | Spearman={spear:.2f}", y=1.02)
    plt.tight_layout()
    plt.savefig(output_dir / f"{nome_arquivo}.png", dpi=200)
    plt.close()
    print(f"[✔] {titulo} -> {nome_arquivo}.png")

# ============================================================
#                     GRÁFICOS RQ A (Feedback Final)
# ============================================================

# RQ01 - tamanho PRs x feedback final
plot_hex("total_lines", "_status_code",
          "Tamanho Total (linhas)", "Feedback Final (código)",
          "RQ01 - Relação entre tamanho dos PRs e feedback final",
          "RQ01_tamanho_feedback")

# RQ02 - tempo análise x feedback final
plot_hex("analysis_time_hours", "_status_code",
          "Tempo de Análise (h)", "Feedback Final (código)",
          "RQ02 - Relação entre tempo de análise e feedback final",
          "RQ02_tempo_feedback")

# RQ03 - descrição x feedback final
plot_hex("desc_len", "_status_code",
          "Tamanho da Descrição", "Feedback Final (código)",
          "RQ03 - Relação entre descrição e feedback final",
          "RQ03_descricao_feedback")

# RQ04 - interações x feedback final
plot_hex("comments_count", "_status_code",
          "Interações (comentários)", "Feedback Final (código)",
          "RQ04 - Relação entre interações e feedback final",
          "RQ04_interacoes_feedback")

# ============================================================
#                   GRÁFICOS RQ B (Nº de Revisões)
# ============================================================

# RQ05 - tamanho PRs x nº revisões
plot_hex("total_lines", "num_reviews",
          "Tamanho Total (linhas)", "Número de Revisões",
          "RQ05 - Relação entre tamanho dos PRs e nº de revisões",
          "RQ05_tamanho_revisoes")

# RQ06 - tempo análise x nº revisões
plot_hex("analysis_time_hours", "num_reviews",
          "Tempo de Análise (h)", "Número de Revisões",
          "RQ06 - Relação entre tempo de análise e nº de revisões",
          "RQ06_tempo_revisoes")

# RQ07 - descrição x nº revisões
plot_hex("desc_len", "num_reviews",
          "Tamanho da Descrição", "Número de Revisões",
          "RQ07 - Relação entre descrição e nº de revisões",
          "RQ07_descricao_revisoes")

# RQ08 - interações x nº revisões
plot_hex("comments_count", "num_reviews",
          "Interações (comentários)", "Número de Revisões",
          "RQ08 - Relação entre interações e nº de revisões",
          "RQ08_interacoes_revisoes")

# ============================================================
#                     RESUMO FINAL
# ============================================================

print(f"\n[✅] Gráficos salvos em: {output_dir.resolve()}")
