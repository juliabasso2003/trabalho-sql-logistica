# Trabalho SQL Logística — Smart Talent John Deere

Projeto do tema 4 (Logística/Materiais: rastreamento, estoque e atrasos) do
programa Smart Talent, no Instituto Caldeira.

A pergunta é onde e por que os materiais atrasam. A base é o
[DataCo Smart Supply Chain](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis),
com 180.519 pedidos e 53 colunas. A entrega é um dashboard em Power BI que lê de
uma camada de dados montada no Databricks.

---

## Por onde o dado passa

```
CSV no repositório
        │
        ├──► Databricks ─► tabela (Delta) ─► vw_enviados ─► 5 tabelas bi_* ─► Power BI
        │
        └──► pipeline.py (pandas + Docker) ─► output/
```

São dois caminhos separados. O de cima é a solução. O de baixo é a análise que
fizemos antes de migrar pro Databricks, e continua aqui porque mostra como a
gente chegou nas perguntas.

---

## Os arquivos

| Arquivo | O que faz |
|---|---|
| `src/camada_bi.ipynb` | Carrega o CSV como tabela Delta e cria a view e as 5 tabelas que o Power BI consome. Roda sozinho. |
| `src/ETL CSV.ipynb` | Consultas de exploração da base, feitas antes de fechar a camada. |
| `src/modelo_ml.ipynb` | Modelo baseline de previsão de atraso. Gera `src/output/metricas.json`. |
| `src/pipeline.py` | Pipeline em pandas. Lê o CSV e gera tabelas e gráficos em `output/`. |
| `data/` | O CSV. |
| `output/` | Saídas do `pipeline.py`. |

---

## A camada do Power BI

As consultas do `ETL CSV` criam `enviados` como TEMP VIEW. TEMP quer dizer que
ela existe só dentro da sessão que criou, e o Power BI abre a própria sessão
contra o warehouse — então ele não acha a view e nenhuma consulta roda a partir
do dashboard.

O `camada_bi.ipynb` resolve isso salvando os mesmos resultados de verdade:

| Objeto | Linhas | Para quê |
|---|---|---|
| `vw_enviados` | — | Base das outras. Tira os cancelados e calcula a flag de atraso e a data do pedido. |
| `bi_geral` | 1 | Os números do topo do dashboard. |
| `bi_modo_envio` | 4 | Prazo prometido contra prazo real, por modo de envio. |
| `bi_quebras` | 193 | Dez quebras numa tabela só, no formato `dimensao / valor / taxa`: região, estado, cidade, mercado, categoria, segmento, tipo de pagamento, status, qtd de itens e dia da semana. No BI isso vira um gráfico com filtro em vez de dez gráficos quase iguais. |
| `bi_serie_mensal` | 37 | Atraso mês a mês. |
| `bi_faixa_valor` | 4 | Atraso por faixa de valor do pedido. |

São 239 linhas no total, contra 172.765 da tabela bruta.

### Rodando

1. No Databricks, clone o repositório como Git folder e escolha a branch.
2. Rode o `camada_bi.ipynb` de cima para baixo. A primeira célula lê o CSV e
   grava a `tabela`, e imprime a contagem: tem que dar 180519. As seis seguintes
   criam a view e as cinco tabelas.
3. Confira com `SELECT * FROM bi_geral` — tem que dar 172.765 pedidos, 98.977
   atrasados e 57,3% de taxa de atraso.

### Conectando o Power BI

Obter dados → Databricks → informe o server hostname e o HTTP path do SQL
warehouse → autenticação por Personal Access Token. Importe as 5 tabelas `bi_*`,
não a tabela bruta.

---

## O que os dados mostram

A taxa geral de atraso é 57,3%: 98.977 de 172.765 pedidos enviados.

Medimos quanto cada dimensão separa o atraso, contando só grupos com 300 pedidos
ou mais:

| Dimensão | Menor | Maior | Amplitude |
|---|---|---|---|
| Modo de envio | 39,8% | 100,0% | 60,2 pts |
| Cidade do cliente | 49,6% | 66,8% | 17,2 pts |
| Estado do cliente | 52,6% | 63,0% | 10,4 pts |
| Categoria | 52,7% | 62,6% | 9,9 pts |
| Região | 51,6% | 60,1% | 8,5 pts |
| Status do pedido | 55,6% | 57,9% | 2,3 pts |
| Dia da semana | 56,6% | 57,8% | 1,2 pts |
| Mercado | 56,8% | 57,7% | 0,9 pt |
| Tipo de pagamento | 56,6% | 57,5% | 0,9 pt |
| Qtd. de itens | 56,9% | 57,6% | 0,7 pt |
| Segmento | 57,1% | 57,6% | 0,5 pt |

Mês a mês fica entre 56,7% e 58,0%, e por faixa de valor entre 57,0% e 57,7%.
Nem época do ano nem valor do pedido explicam o atraso.

Só o modo de envio separa, e separa porque o prazo prometido é fixo por modo:

| Modo | Prometido | Real médio | Taxa de atraso | Pedidos |
|---|---|---|---|---|
| First Class | 1 dia | 2,00 dias | 100,0% | 26.513 |
| Second Class | 2 dias | 3,99 dias | 79,8% | 33.806 |
| Same Day | 0 dias | 0,48 dia | 47,9% | 9.293 |
| Standard Class | 4 dias | 3,99 dias | 39,8% | 103.153 |

No First Class a diferença mínima é igual à máxima, 1 dia, nos 26.513 pedidos:
nenhum chegou no prazo, e sempre pelo mesmo um dia. Já o Standard Class entrega
em 3,99 dias contra 4 prometidos, ou seja, cumpre o prazo na média.

Com isso, o atraso não parece ser problema de operação. A entrega leva uns 2
dias e varia pouco. O que varia é o prazo que foi prometido: quem promete 1 dia
erra sempre, quem promete 4 acerta.

---

## Coisas da base que vale saber

`Late_delivery_risk` não é um risco previsto, é o resultado. Nos 172.765 pedidos
enviados, ela vale 1 em todos os 98.977 `Late delivery` e em nenhum pedido
entregue no prazo. Por isso não entra na camada do BI, e o `modelo_ml.ipynb`
deixa ela de fora: usar como variável seria dar a resposta pro modelo.

`Delivery_Status = 'Late delivery'` dá no mesmo que `dias_real > dias_prog`, nos
98.977 casos. As duas formas de definir atraso são a mesma coisa.

Agrupar por mês precisa do ano junto. A base vai de janeiro de 2015 a janeiro de
2018, então agrupar só por `MONTH()` soma quatro janeiros contra três dos outros
meses. A `bi_serie_mensal` usa ano e mês.

O `NTILE` da faixa de valor precisa de desempate. `Sales` tem 180.519 linhas e só
193 valores distintos, com um empate de 22.372 linhas no mesmo valor. Sem
desempate o corte do quartil cai no meio de um bloco de valores iguais e cada
execução devolve número diferente, então a consulta usa
`ORDER BY Sales, Order_Item_Id`.

---

## O modelo de ML

O `modelo_ml.ipynb` treina um Random Forest pra prever se um pedido vai atrasar,
usando só o que já se sabe no momento do pedido: modo de envio, região, mercado,
categoria, tipo de pagamento, segmento, prazo programado, quantidade, mês e dia
da semana. Treino e teste são separados por período, não sorteados: os 80% mais
antigos treinam e os 20% mais recentes testam.

O resultado fica em `src/output/metricas.json`: acurácia 0,694 contra 0,573 de um
baseline que chuta que todo pedido atrasa.

---

## Pipeline local em Docker

Essa parte é da análise que veio antes do Databricks e não alimenta o dashboard.

O `src/pipeline.py` lê o CSV com pandas, responde as perguntas de negócio da
semana 2 e grava tabelas em `.csv` e gráficos em `.png` na pasta `output/`.

### Com Docker

```
docker compose up --build
```

O `compose.yaml` já monta `data/` e `output/` como volumes. Para remover o
container depois, `docker compose down`.

### Sem Docker

```
python -m venv venv
.\venv\Scripts\Activate.ps1      # PowerShell
pip install -r requirements.txt
python src/pipeline.py
```

### Como saber se deu certo

O terminal imprime quatro consultas, começando por:

```
=== PERGUNTA 3: taxa de atraso por modo ===
          modo  total_pedidos  atrasados  taxa_atraso_pct
   First Class          26513      26513            100.0
  Second Class          33806      26987             79.8
      Same Day           9293       4454             47.9
Standard Class         103153      41023             39.8
```

E a pasta `output/` fica com `taxa_atraso_por_modo.csv`,
`prazo_programado_x_real.csv`, `resumo_atraso_prazo.csv`,
`distribuicao_prazo_real.csv`, `tempo_medio_entrega_por_cidade_top10.csv`,
`atraso_por_regiao.csv` e os quatro `.png` correspondentes.

### Imagem no Docker Hub

A imagem está publicada como
`marcoantoniodecarlirodegheri/trabalho-sql-logistica`. Para rodar em outra
máquina sem o código, crie uma pasta com `data/` e `output/` dentro, ponha o CSV
em `data/` e rode:

```
docker pull marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1
docker run --rm -v "${PWD}\data:/app/data" -v "${PWD}\output:/app/output" marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1
```

No Mac ou Linux, troque `${PWD}\data` por `$(pwd)/data`.

---

## Equipe

Grupo 2 — Júlia Basso Agazzi, Lucas Santos, Marco Antônio De Carli Rodegheri,
Nicoly Carvalho, Otávio Fogaça da Rosa.
