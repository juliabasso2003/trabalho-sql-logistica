import matplotlib.pyplot as plt
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

# PERGUNTA: o atraso depende da região para onde o pedido vai?
# Tiramos os pedidos cancelados, igual nas outras consultas, porque eles nem chegaram a ser enviados
pedidos = df[df['Delivery Status'] != 'Shipping canceled'].copy()
pedidos['atrasado'] = (pedidos['Delivery Status'] == 'Late delivery').astype(int)  # 1 = atrasou, 0 = não

atraso_regiao = (
    pedidos.groupby('Order Region')
    .agg(
        total_pedidos=('atrasado', 'size'),   # quantos pedidos foram para a região
        atrasados=('atrasado', 'sum'),        # quantos desses atrasaram
    )
    .reset_index()
)
atraso_regiao['taxa_atraso_pct'] = (atraso_regiao['atrasados'] / atraso_regiao['total_pedidos'] * 100).round(1)
atraso_regiao = atraso_regiao.sort_values('taxa_atraso_pct', ascending=False)

# média de todos os pedidos, para comparar cada região com o geral
media_geral = round(pedidos['atrasado'].mean() * 100, 1)

print('\n=== PERGUNTA: taxa de atraso por região ===')
print(atraso_regiao.to_string(index=False))
print(f'Média geral de atraso: {media_geral}%')

atraso_regiao.to_csv(PASTA_SAIDA / 'atraso_por_regiao.csv', index=False)

# Gráfico: eixo de 0 a 100% para dar para ver que as barras ficam todas parecidas
plt.figure(figsize=(9, 7))
plt.barh(
    atraso_regiao['Order Region'].iloc[::-1],
    atraso_regiao['taxa_atraso_pct'].iloc[::-1],
    color='steelblue',
)
plt.axvline(media_geral, color='red', linestyle='--', label=f'Média geral ({media_geral}%)')
plt.title('Todas as regiões atrasam mais da metade dos pedidos:\no destino não explica o atraso')
plt.xlabel('Taxa de atraso (%)')
plt.ylabel('Região')
plt.xlim(0, 100)
plt.legend()
plt.tight_layout()
plt.savefig(PASTA_SAIDA / 'atraso_por_regiao.png', dpi=150)
plt.close()

print(f'Tabela e gráfico da região salvos em: {PASTA_SAIDA}')
