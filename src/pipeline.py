import pandas as pd

df = pd.read_csv(r'C:\smart_talent - aula 2\trabalho-sql-logistica\data\DataCoSupplyChainDataset.csv', encoding='latin1')

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

df = df[colunas]
print(df)