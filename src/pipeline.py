import pandas as pd
import sqlite3 as sql

df = pd.read_csv(r'C:\Users\Júlia Agazzi\trabalho-sql-logistica\data\DataCoSupplyChainDataset.csv', encoding='latin1')

# Seleciona somente a coluna Type
print(df[['Days for shipping (real)']])