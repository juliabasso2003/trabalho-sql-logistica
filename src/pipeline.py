import pandas as pd
from pathlib import Path

# Pasta raiz do projeto (um nível acima de src/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Caminho para o arquivo de dados e pasta de saída
CAMINHO = BASE_DIR / 'data' / 'DataCoSupplyChainDataset.csv'
PASTA_SAIDA = BASE_DIR / 'output'

# Cria a pasta de saída, caso não exista
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

colunas = [
    # Grupo 1
    "Late_delivery_risk",
    "Delivery Status",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Shipping Mode",
    "order date (DateOrders)",
    "shipping date (DateOrders)",
    # Grupo 2
    "Order Region",
    "Order Country",
    "Category Name",
    "Department Name",
    "Type",
    "Order Status",
]

df = pd.read_csv(CAMINHO, encoding='latin1', usecols=colunas)

df.to_csv(PASTA_SAIDA / 'dados_filtrados.csv', index=False)
print(f'{len(df)} linhas salvas em: {PASTA_SAIDA}')