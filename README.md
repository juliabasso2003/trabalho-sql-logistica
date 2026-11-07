# Trabalho-sql-logistica

Trabalho de SQL sobre atrasos na logística (Smart Logistics).

O objetivo é descobrir onde os materiais atrasam. O pipeline (`src/pipeline.py`) lê a base `DataCoSupplyChainDataset.csv`, separa só as colunas para análise e salva o resultado em `output/dados_filtrados.csv`. Depois disso ele responde as perguntas de negócio do grupo (explicadas mais abaixo, em [Perguntas de negócio](#perguntas-de-negócio)), gerando tabelas e gráficos na pasta `output/`.

O projeto roda dentro de um container Docker, então não é preciso ter Python nem as bibliotecas instaladas na máquina. Os dados não ficam dentro da imagem: eles entram por volume na hora de rodar.

---

## Estrutura do projeto

```
trabalho-sql-logistica/
├── data/                  # coloque o CSV aqui (não vai para a imagem)
├── output/                # onde o resultado é salvo
├── src/
│   └── pipeline.py        # script do pipeline
├── requirements.txt       # bibliotecas Python usadas
├── Dockerfile             # receita da imagem
├── .dockerignore          # o que NÃO vai para a imagem
└── compose.yaml           # atalho para build + run
```

---

## Como baixar o projeto

```
git clone https://github.com/juliabasso2003/trabalho-sql-logistica.git
cd trabalho-sql-logistica
```

---

## Antes de rodar

1. Ter o Docker Desktop instalado e aberto. Para testar: `docker --version`.
2. Baixar o dataset no Kaggle: [DataCo Smart Supply Chain](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis). Dele, só é usado o arquivo `DataCoSupplyChainDataset.csv`.
3. Criar a pasta `data/` na raiz do projeto e colocar o `DataCoSupplyChainDataset.csv` dentro dela. O nome tem que ser exatamente esse, com as mesmas maiúsculas.

```
mkdir data
```

A pasta `data/` não vem no repositório porque os dados são grandes e ficam fora do Git (estão no `.gitignore`). A pasta `output/` não precisa ser criada: ela é criada sozinha quando o pipeline roda.

---
## Rodando com o código

Para quem baixou o projeto do GitHub. A imagem é montada na própria máquina a partir do Dockerfile.

### Forma 1: com Docker Compose (mais simples)

Na pasta do projeto, rode:

```
docker compose up --build
```

O `--build` monta a imagem antes de rodar. Ele é necessário na primeira vez e sempre que o `pipeline.py` for alterado. Nas outras vezes basta:

```
docker compose up
```

O `compose.yaml` já tem configurados os volumes de `data/` e `output/`, então não precisa passar caminho nenhum. 

Para remover o container depois que ele termina:

```
docker compose down
```

---

### Forma 2: com `docker build` e `docker run`

#### Build (criar a imagem)

```
docker build -t trabalho-sql-logistica .
```

- `-t trabalho-sql-logistica`: nome da imagem.
- `.`: usa a pasta atual (onde está o Dockerfile). O ponto é obrigatório.

#### Run (rodar o pipeline)

PowerShell:

```
docker run --rm -v "${PWD}\data:/app/data" -v "${PWD}\output:/app/output" trabalho-sql-logistica
```

No Mac ou Linux, troque `${PWD}\data` por `$(pwd)/data` (e o mesmo para `output`).

O que cada parte faz:

- `-v "...\data:/app/data"`: o volume de entrada. A pasta `data/` do computador aparece dentro do container como `/app/data`, e é por ela que o CSV entra.
- `-v "...\output:/app/output"`: o volume de saída. O arquivo que o script gera em `/app/output` aparece na pasta `output/` do computador.
- `--rm`: apaga o container quando ele termina, para não ficar acumulando.
- As aspas são necessárias quando o caminho da pasta tem espaço.

#### Como saber se deu certo

O terminal mostra uma saída parecida com esta (a tabela da região aparece inteira, aqui está resumida):

```
180519 linhas salvas em: /app/output

=== PERGUNTA: taxa de atraso por região ===
   Order Region  total_pedidos  atrasados  taxa_atraso_pct
 Central Africa           1616        972             60.1
 ...
         Canada            907        468             51.6
Média geral de atraso: 57.3%
Tabela e gráfico da região salvos em: /app/output
```

E aparecem na pasta `output/` os arquivos `dados_filtrados.csv`, `atraso_por_regiao.csv` e `atraso_por_regiao.png`.

---

## Rodando sem o código (imagem do Docker Hub)

A imagem também foi publicada no Docker Hub, para rodar em outra máquina sem precisar do código.

### Para publicar a imagem (só quem mantém a imagem)

```
docker login
docker tag trabalho-sql-logistica marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1
docker push marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1
```

A imagem está publicada no Docker Hub como `marcoantoniodecarlirodegheri/trabalho-sql-logistica` (repositório público). A versão mais nova é a `1.1`, que já tem a consulta de atraso por região. Quando o pipeline mudar, é só publicar com um número novo (`1.2`, `1.3`...). Para publicar em outra conta, troque o usuário nos comandos acima.

Se a imagem for rodar em um Mac com chip M1/M2/M3, ela precisa ser publicada para as duas arquiteturas. Nesse caso, use este comando no lugar do `tag` e do `push` (ele já faz o build e o envio juntos):

```
docker buildx build --platform linux/amd64,linux/arm64 -t marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1 --push .
```

### Para rodar (outro grupo)

1. Criar uma pasta com duas subpastas, `data/` e `output/`.
2. Colocar o `DataCoSupplyChainDataset.csv` dentro de `data/`.
3. Dentro dessa pasta geral, rodar (PowerShell):

```
docker pull marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1
docker run --rm -v "${PWD}\data:/app/data" -v "${PWD}\output:/app/output" marcoantoniodecarlirodegheri/trabalho-sql-logistica:1.1
```

No Mac ou Linux, troque `${PWD}\data` por `$(pwd)/data` (e o mesmo para `output`).

O resultado aparece na pasta `output/` dessa máquina (os mesmos arquivos da seção [Como saber se deu certo](#como-saber-se-deu-certo)).

---

## Rodando sem Docker (opcional)

Para testar o script direto no computador:

```
python -m venv venv
.\venv\Scripts\Activate.ps1      # PowerShell
# source venv/Scripts/activate   # bash no Windows
pip install -r requirements.txt
python src/pipeline.py
```

O script encontra as pastas `data/` e `output/` a partir de onde ele mesmo está (`Path(__file__)`). Por isso o mesmo código funciona no computador e dentro do container sem nenhuma alteração.

---

## Sobre os arquivos do Docker

**Dockerfile**

| Linha | O que faz |
|---|---|
| `FROM python:3.12-slim` | Usa uma imagem Linux enxuta já com Python 3.12 (mesma versão usada no desenvolvimento) |
| `WORKDIR /app` | Define `/app` como pasta de trabalho dentro do container |
| `COPY requirements.txt .` | Copia a lista de bibliotecas |
| `RUN pip install --no-cache-dir -r requirements.txt` | Instala as bibliotecas (vem antes do código para aproveitar o cache do Docker) |
| `COPY src/ ./src/` | Copia só o código. Os dados não são copiados |
| `CMD ["python", "src/pipeline.py"]` | Comando que roda quando o container inicia |

**.dockerignore**

Evita que a venv, o `.git`, os CSVs e a pasta `output/` sejam enviados para o build. Assim a imagem fica menor, o build fica mais rápido e os dados realmente só entram por volume.

---

## Perguntas de negócio

### O atraso depende da região para onde o pedido vai?

**Por que essa pergunta:** o tema do trabalho é descobrir onde os materiais atrasam. Antes de olhar para cidades ou produtos, a gente quis ver se existe alguma região do mundo que concentra os atrasos, porque se existisse, o problema poderia estar no destino (distância, transporte local, etc).

**Como foi feito:**
- Tiramos os pedidos com status `Shipping canceled`, porque eles nem chegaram a ser enviados, então não faz sentido dizer se atrasaram ou não.
- Criamos a coluna `atrasado`, que vale 1 quando o `Delivery Status` é `Late delivery` e 0 nos outros casos.
- Agrupamos por `Order Region` e calculamos o total de pedidos, quantos atrasaram e a taxa de atraso em %.
- Calculamos também a média geral de atraso de todos os pedidos, para comparar cada região com ela.

**Resultado:** a média geral de atraso é de 57,3%, e todas as 23 regiões ficam perto disso, entre 51,6% (Canada) e 60,1% (Central Africa). Ou seja, todas as regiões atrasam mais da metade dos pedidos e nenhuma se destaca muito das outras. A conclusão é que o destino não explica o atraso: ele está espalhado igual pelo mundo todo, então a causa tem que estar em outra coisa (como o modo de envio).

**Arquivos gerados:**
- `output/atraso_por_regiao.csv`: tabela com total de pedidos, atrasados e taxa de atraso por região
- `output/atraso_por_regiao.png`: gráfico de barras com a taxa de cada região e uma linha marcando a média geral
