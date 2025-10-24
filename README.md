
# 📝 Relatório Técnico de Laboratório

## 1. Informações do grupo
- **🎓 Curso:** Engenharia de Software
- **📘 Disciplina:** Laboratório de Experimentação de Software
- **🗓 Período:** 6° Período
- **👨‍🏫 Professor(a):** Prof. Dr. João Paulo Carneiro Aramuni
- **👥 Membros do Grupo:** Matheus Hoske, Thiago Perdigão, Ryan Cristian, Samuel Almeida

---

## 2. Introdução
O objetivo deste laboratório é analisar a atividade de code review desenvolvida em repositórios populares do GitHub, identificando variáveis que influenciam no merge de um PR, sob a perspectiva de desenvolvedores que submetem código aos repositórios selecionados.

### 2.1. Questões de Pesquisa (Research Questions – RQs)
As **Questões de Pesquisa** foram definidas para guiar a investigação e estruturar a análise dos dados coletados:

**🔍 Questões de Pesquisa - Research Questions (RQs):**
**A. Feedback Final das Revisões (Status do PR):**

| RQ   | Pergunta |
|------|----------|
| RQ01 | Qual a relação entre o tamanho dos PRs e o feedback final das revisões? |
| RQ02 | Qual a relação entre o tempo de análise dos PRs e o feedback final das revisões? |
| RQ03 | Qual a relação entre a descrição dos PRs e o feedback final das revisões? |
| RQ04 | RQ 04. Qual a relação entre as interações nos PRs e o feedback final das revisões? |

**B. Número de Revisões:**

| RQ   | Pergunta |
|------|----------|
| RQ05 | Qual a relação entre o tamanho dos PRs e o número de revisões realizadas? |
| RQ06 | Qual a relação entre o tempo de análise dos PRs e o número de revisões realizadas? |
| RQ07 | Qual a relação entre a descrição dos PRs e o número de revisões realizadas? |
| RQ08 | Qual a relação entre as interações nos PRs e o número de revisões realizadas? |

### 2.2. Hipóteses Informais (Informal Hypotheses – IH)
As **Hipóteses Informais** foram elaboradas a partir das RQs, estabelecendo expectativas sobre os resultados esperados do estudo:

**💡 Hipóteses Informais - Informal Hypotheses (IH):**

| IH   | Descrição |
|------|-----------|
| IH01 | PRs maiores (com mais linhas de código alteradas) têm maior probabilidade de receber **feedback negativo** (PR fechado sem merge), devido ao aumento da complexidade e do risco de introdução de erros. |
| IH02 | PRs com **maior tempo de análise** tendem a ser **aceitos (merged)** com mais frequência, pois o tempo adicional reflete revisões mais cuidadosas e discussões detalhadas. |
| IH03 | PRs com **descrições mais detalhadas e completas** apresentam **maior taxa de aprovação**, pois facilitam o entendimento do contexto e da motivação das mudanças pelos revisores. |
| IH04 | PRs com **maior número de comentários e interações** têm maior chance de **serem aceitos**, indicando um processo de revisão colaborativo e construtivo. |
| IH05 | PRs maiores demandam **mais rodadas de revisão**, uma vez que alterações extensas exigem múltiplas iterações até atender aos padrões de qualidade do projeto. |
| IH06 | PRs com **maior tempo total de análise** apresentam também **mais revisões**, refletindo ciclos mais longos de feedback e retrabalho. |
| IH07 | PRs com **descrições curtas ou vagas** tendem a exigir **mais revisões**, já que a falta de clareza pode gerar dúvidas e solicitações adicionais de esclarecimento. |

---

## 3. Tecnologias e ferramentas utilizadas
- **💻 Linguagem de Programação:** Python
- **🛠 Frameworks/Bibliotecas:** Pandas
- **🌐 APIs utilizadas:** GitHub GraphQL API, GitHub REST API
- **📦 Dependências:** requests

---

## 4. Metodologia

### 4.1 Coleta de dados

A coleta de dados foi realizada de forma automatizada por meio da **API GraphQL do GitHub**, utilizando um **token de acesso pessoal** com permissão de leitura pública (`public_repo`).  
O script inicia sua execução buscando os **200 repositórios mais populares do GitHub** (ordenados por número de estrelas) e seleciona apenas aqueles que possuem **pelo menos 100 Pull Requests (PRs)** com status `MERGED` ou `CLOSED`.

Essa etapa é implementada pela função:

`buscar_repositorios_elegiveis(total_repos=200, min_prs=100)` 

Durante essa fase, o script:

-   Realiza consultas paginadas à API GraphQL para coletar metadados sobre repositórios;
    
-   Aplica o filtro mínimo de 100 PRs totais;
    
-   Armazena uma lista de repositórios “elegíveis” para análise.
    

Em seguida, a coleta detalhada dos Pull Requests é feita pela função:

`coletar_dados_pull_requests(repositorios, max_prs_por_repositorio=50)` 

Essa função busca informações específicas sobre cada PR dos repositórios elegíveis, incluindo:

-   **Estado final (merged/closed);**
    
-   **Datas de criação, fechamento e merge;**
    
-   **Número de linhas adicionadas e removidas;**
    
-   **Número de arquivos modificados;**
    
-   **Quantidade de revisões, comentários e participantes;**
    
-   **Texto descritivo do PR.**
    

Cada PR retornado é processado e armazenado em uma lista de dicionários, posteriormente exportada como um arquivo CSV (`dados_pull_requests_analise.csv`).

---

### 4.2 Filtragem e paginação
Para garantir a qualidade e relevância dos dados, o script aplica filtros de elegibilidade diretamente durante a coleta:

1.  **PRs devem possuir pelo menos uma revisão (`reviews.totalCount ≥ 1`)** — garantindo que houve participação humana no processo de code review;
    
2.  **PRs devem ter sido revisados por pelo menos uma hora** — calculado pela diferença entre `createdAt` e `mergedAt/closedAt`, filtrando revisões automáticas (por bots de CI/CD);
    
3.  **Somente PRs com status `MERGED` ou `CLOSED` são analisados.**
    

A coleta é feita de forma paginada (GraphQL cursor-based pagination), garantindo que todos os PRs de cada repositório sejam acessados gradualmente sem exceder os limites de requisição da API.  
Além disso, é possível configurar o número máximo de PRs coletados por repositório por meio do parâmetro:

`LIMITE_POR_REPOSITORIO = 50` 

permitindo ajustar o volume de dados conforme a capacidade de armazenamento ou tempo de execução disponível.

---

### 4.3 Normalização e pré-processamento
Após a coleta, os dados são **estruturados e normalizados** em formato tabular (DataFrame do Pandas) e exportados em `.csv` com codificação UTF-8.  
Durante esse processo, o script:

-   **Converte timestamps ISO 8601** em objetos `datetime` padronizados para o fuso UTC;
    
-   **Calcula o tempo total de análise do PR em horas**, derivado da diferença entre as datas de criação e fechamento/merge;
    
-   **Transforma textos de descrição em métricas quantitativas**, como o número de caracteres (`descricao_caracteres`);
    
-   **Remove registros incompletos**, garantindo que apenas PRs com dados válidos sejam incluídos na amostra final.
    

O resultado final é um dataset padronizado, pronto para análise estatística e aplicação de modelos de correlação entre métricas de PRs e os resultados de revisão.

---

### 4.4 Métricas

Inclua métricas relevantes de repositórios do GitHub, separando **métricas do laboratório** e **métricas adicionais trazidas pelo grupo**:

#### 📊 Métricas de Laboratório - Lab Metrics (LM)
| Código | Métrica | Descrição |
|--------|---------|-----------|
| LM01 | 🕰 Idade do Repositório (anos) | Tempo desde a criação do repositório até o momento atual, medido em anos. |
| LM02 | ✅ Pull Requests Aceitas | Quantidade de pull requests que foram aceitas e incorporadas ao repositório. |
| LM03 | 📦 Número de Releases | Total de versões ou releases oficiais publicadas no repositório. |
| LM04 | ⏳ Tempo desde a Última Atualização (dias) | Número de dias desde a última modificação ou commit no repositório. |
| LM05 | 📋 Percentual de Issues Fechadas (%) | Proporção de issues fechadas em relação ao total de issues criadas, em percentual. |
| LM06 | ⭐ Número de Estrelas | Quantidade de estrelas recebidas no GitHub, representando interesse ou popularidade. |
| LM07 | 🍴 Número de Forks | Número de forks, indicando quantas vezes o repositório foi copiado por outros usuários. |
| LM08 | 📏 Tamanho do Repositório (LOC) | Total de linhas de código (Lines of Code) contidas no repositório. |

#### 💡 Métricas adicionais trazidas pelo grupo - Additional Metrics (AM)
| Código | Métrica | Descrição |
|--------|---------|-----------|
| AM01 | tempo_analise_horas | Tempo total entre a criação e o fechamento/merge do PR (em horas) |
| AM02 | interacoes_participantes | Número de usuários distintos que interagiram no PR (comentários, revisões, etc.) |
| AM03 | interacoes_comentarios | Total de comentários registrados no PR |
| AM04 | tamanho_total_linhas | Soma de linhas adicionadas e removidas (`additions + deletions`) |
---

### 4.5 Cálculo de métricas
Após a coleta e normalização dos dados, foram calculadas as seguintes **métricas principais** para cada _Pull Request (PR)_:

| Categoria | Métrica | Nome da Variável | Descrição |
|:-----------|:----------|:----------------|:------------|
| **Feedback Final** | `status_final` | Estado final do PR (`MERGED` ou `CLOSED`) | Indica se o PR foi aceito ou rejeitado após revisão |
| **Tempo de Análise** | `tempo_analise_horas` | Tempo total (em horas) entre a criação e o fechamento/merge do PR | Mede a duração do ciclo de revisão |
| **Tamanho do PR** | `tamanho_total_linhas` | Soma das linhas adicionadas e removidas (`additions + deletions`) | Indica o volume total de modificações |
| **Interações – Participantes** | `interacoes_participantes` | Quantidade de usuários únicos que participaram do PR (comentários, revisões, etc.) | Mede o nível de engajamento colaborativo |
| **Interações – Comentários** | `interacoes_comentarios` | Total de comentários deixados durante o processo de revisão | Representa a intensidade de discussão no PR |
| **Número de Revisões** | `numero_revisoes` | Total de rodadas de revisão registradas no PR | Indica a profundidade e complexidade do processo de análise |


---

### 4.6 Ordenação e análise inicial
Após o cálculo das métricas, foi realizada uma **análise exploratória inicial** dos dados, com o objetivo de identificar tendências e padrões preliminares.

As principais etapas dessa fase foram:

1.  **Ordenação dos PRs por métricas-chave:**
    
    -   Por `tempo_analise_horas`, para observar a distribuição do tempo de revisão;
        
    -   Por `tamanho_total_linhas`, para identificar PRs com grandes volumes de alteração;
        
    -   Por `interacoes_comentarios` e `interacoes_participantes`, para verificar padrões de engajamento;
        
    -   Por `numero_revisoes`, para detectar casos de múltiplas iterações de feedback.
        
2.  **Análise descritiva:**  
    Foram calculadas estatísticas básicas (média, mediana, desvio padrão e quartis) para cada métrica, além de histogramas e boxplots para visualizar a dispersão dos valores.
    
3.  **Verificação de consistência:**
    
    -   PRs com valores inconsistentes (ex.: tempo negativo) foram descartados;
        
    -   Foram observadas correlações visuais preliminares entre tamanho, tempo e interações.
        

Essas análises iniciais serviram para **entender o comportamento geral do dataset** antes das correlações formais entre as variáveis e as questões de pesquisa (RQs).

---

### 4.7. Relação das RQs com as Métricas

A seguir, apresenta-se a relação entre as **Questões de Pesquisa (RQs)** e as **métricas selecionadas** — tanto padrão quanto adicionais — que serão utilizadas para responder cada uma delas.

**🔍 Relação das RQs com Métricas:**

| ID | Questão de Pesquisa (RQ) | Métricas Utilizadas | Tipo de Relação Analisada |
|:---|:---------------------------|:--------------------|:---------------------------|
| **RQ1** | Qual a relação entre o **tamanho dos PRs** e o **feedback final das revisões**? | `tamanho_total_linhas`, `status_final` | Avaliar se PRs maiores têm menor taxa de merge |
| **RQ2** | Qual a relação entre o **tempo de análise dos PRs** e o **feedback final das revisões**? | `tempo_analise_horas`, `status_final` | Verificar se revisões mais longas tendem a resultar em merge |
| **RQ3** | Qual a relação entre as **interações nos PRs** e o **feedback final das revisões**? | `interacoes_participantes`, `interacoes_comentarios`, `status_final` | Medir se PRs com mais engajamento têm maior chance de aceitação |
| **RQ5** | Qual a relação entre o **tamanho dos PRs** e o **número de revisões realizadas**? | `tamanho_total_linhas`, `numero_revisoes` | Testar se PRs maiores exigem mais rodadas de revisão |
| **RQ6** | Qual a relação entre o **tempo de análise dos PRs** e o **número de revisões realizadas**? | `tempo_analise_horas`, `numero_revisoes` | Investigar se revisões mais longas têm mais iterações |
| **RQ8** | Qual a relação entre as **interações nos PRs** e o **número de revisões realizadas**? | `interacoes_participantes`, `interacoes_comentarios`, `numero_revisoes` | Avaliar se o aumento das interações está ligado a mais revisões |


---

## 5. Resultados

### Análise dos Resultados: Heatmaps de Métricas de Pull Requests

Esta análise explora a relação entre as características dos Pull Requests (PRs) — medidas por variáveis de Tamanho, Tempo de Análise, Descrição e Interações — e seus resultados, conforme definido nas Questões de Pesquisa (RQs).

Os resultados são apresentados em três heatmaps que fornecem perspectivas complementares sobre as relações de dados.

### 1. Heatmap de Correlação entre Métricas

![Correlação entre métricas](graficos_heatmap/heatmap_correlacoes_metricas.png)

Este gráfico quantifica a relação linear (Correlação de Pearson) entre todas as métricas numéricas. Os valores variam de **-1** (relação inversa forte) a **+1** (relação direta forte).


| Métrica| Correlação com `num_reviews` | Relação com Outras Métricas |
|:---|:---------------------------|:--------------------|
`total_lines`| **0.13** (Fraca) | Forte correlação com `num_files` (0.64) |
`analysis_time_hours`| **0.16**(Fraca)| Média correlação com `comments_count` (0.24)| `desc_len`| **0.00**(Nula) | Fraca correlação com todas as outras |
`comments_count`| **0.35**(Moderada) | Forte correlação com `participants_count`(0.58)| 
`num_reviews` | **--** | Moderada correlação com Interações (`comments_count`, `participants_count`)
---

**Resposta às RQs (Grupo B: Número de Revisões):**
| RQ | Métrica | Conclusão |
|:---|:---------------------------|:--------------------|
RQ 05 | Tamanho x Nº Revisões | A correlação é fraca. O número de revisões não é fortemente determinado apenas pelo tamanho do PR.
RQ 06 | Tempo x Nº Revisões | A correlação é fraca.
RQ 07 | Descrição x Nº Revisões | A correlação é nula. O tamanho da descrição não influencia linearmente no número de revisões.
RQ 08 | Interações x Nº Revisões | A correlação é moderada. PRs com mais revisões tendem a envolver mais participantes e gerar mais comentários.
---

### 2. Heatmap de Médias por Feedback Final (Status do PR)

Este gráfico compara a média das métricas entre os PRs `merged` (aceitos) e `closed` (fechados/rejeitados). A cor indica a magnitude do valor médio.

![Correlação entre métricas](graficos_heatmap/heatmap_status_final.png)

**Resposta às RQs (Grupo A: Feedback Final)**
| RQ | Métrica | Média(MERGED) | Média(CLOSED) | Conclusão Principal| 
|:---|:---------------------------|:--------------------|:--------------------|:--------------------|
RQ 01 | Tamanho (`total_lines`) | 9360.5 | 20792.8 | **PRs fechados são, em média, mais de duas vezes maiores** do que PRs mesclados. |
RQ 02 | Tempo (`analysis_time_hours`) | 63.8 | 140.7 | **PRs fechados levam, em média, mais do que o dobro do tempo** para análise, sugerindo maior atrito. | 
RQ 03 | Descrição (`desc_len`) | 1073.3 | 1378.1 | **Descrições de PRs fechados são levemente mais longas**, embora a diferença não seja tão acentuada. |
RQ 04 | Interações (`comments_count`) | 3.7 | 10.1 | **PRs fechados geram, em média, quase o triplo de comentários**, indicando muito mais discussão e complexidade/controvérsia. |

---

### 3. Heatmap de Médias por Faixa de Número de Revisões

Este gráfico agrupa os PRs em faixas de número de revisões (e.g., "1", "2-3", "10+") e exibe a média das métricas por faixa. Isso permite visualizar a progressão e o impacto do aumento no número de revisões.

![Correlação entre métricas](graficos_heatmap/heatmap_num_revisoes.png)


### Análise da Progressão (RQs 05 a 08 - Visão Complementar)

A análise da progressão nas faixas de revisão reforça as tendências vistas no Heatmap 1, mas de forma visual:

-   **Tamanho (RQ 05):** A média de `total_lines` e `num_files` mostra uma **tendência clara de aumento** à medida que o número de revisões sobe (e.g., `total_lines` de 7837.2 para 14619.0 na faixa "10+").
    
-   **Tempo de Análise (RQ 06):** Esta é a tendência mais forte. O `analysis_time_hours` **aumenta dramaticamente** de 27.5 horas (1 revisão) para 287.0 horas (10+ revisões), demonstrando que mais revisões resultam em ciclos de desenvolvimento significativamente mais longos.
    
-   **Interações (RQ 08):** O número médio de `comments_count` e `participants_count` **cresce de forma exponencial** com o aumento das revisões, confirmando que a necessidade de mais revisões está ligada a um processo de discussão e colaboração mais intenso.
