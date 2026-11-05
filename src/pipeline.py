import pandas as pd

df = pd.read_csv(r'C:\Users\Júlia Agazzi\trabalho-sql-logistica\data\DataCoSupplyChainDataset.csv', encoding='latin1')

colunas = [
    'Shipping Mode',
    'Delivery Status',
    'Late_delivery_risk',
    'Days for shipping (real)',
    'Days for shipment (scheduled)',
]
df = pd.read_csv(r'C:\Users\Júlia Agazzi\trabalho-sql-logistica\data\DataCoSupplyChainDataset.csv', encoding='latin1', usecols=colunas)

df = df.rename(columns={
    'Shipping Mode': 'modo',
    'Delivery Status': 'status',
    'Late_delivery_risk': 'risco_atraso',
    'Days for shipping (real)': 'dias_real',
    'Days for shipment (scheduled)': 'dias_prog',
    })

con = sql.connect(':memory:')
df.to_sql('pedidos', con, index=False)

#PERGUNT: qual Shipping Mode tem a maior taxa de atraso?
#    (WHERE tira cancelados; GROUP BY agrupa por modo; ORDER BY ordena)
q3 = """
SELECT  modo,
        COUNT(*) AS total_pedidos,
        SUM(CASE WHEN status = 'Late delivery' THEN 1 ELSE 0 END) AS atrasados,
        ROUND(100.0 * SUM(CASE WHEN status = 'Late delivery' THEN 1 ELSE 0 END)
              / COUNT(*), 1) AS taxa_atraso_pct
FROM    pedidos
WHERE   status <> 'Shipping canceled'
GROUP BY modo
ORDER BY taxa_atraso_pct DESC
"""
print('=== PERGUNTA 3: taxa de atraso por modo ===')
print(pd.read_sql(q3, con).to_string(index=False))

#  PERGUNT: o prazo programado é realista?
#    diferença = dias_real - dias_prog  (positivo = demorou mais que o prometido)
q4 = """
SELECT  modo,
        ROUND(AVG(dias_prog), 2)             AS prazo_prog_medio,
        ROUND(AVG(dias_real), 2)             AS prazo_real_medio,
        ROUND(AVG(dias_real - dias_prog), 2) AS diferenca_media,
        MIN(dias_real - dias_prog)           AS menor_diferenca,
        MAX(dias_real - dias_prog)           AS maior_diferenca,
        ROUND(100.0 * SUM(CASE WHEN dias_real > dias_prog THEN 1 ELSE 0 END)
              / COUNT(*), 1)                 AS pct_acima_do_prazo
FROM    pedidos
WHERE   status <> 'Shipping canceled'
GROUP BY modo
ORDER BY diferenca_media DESC
"""
print('\n=== PERGUNTA 4: prazo programado x real ===')
print(pd.read_sql(q4, con).to_string(index=False))

# JOIN: junta as duas análises pela coluna 'modo'
q_join = f"""
SELECT  a.modo, a.total_pedidos, a.taxa_atraso_pct,
        b.prazo_prog_medio, b.prazo_real_medio, b.diferenca_media, b.menor_diferenca
FROM    ({q3}) AS a
JOIN    ({q4}) AS b ON a.modo = b.modo
ORDER BY a.taxa_atraso_pct DESC
"""
print('\n=== RESUMO (JOIN) ===')
print(pd.read_sql(q_join, con).to_string(index=False))
 
# Distribuição: quantos pedidos por combinação prazo x real
q_dist = """
SELECT modo, dias_prog, dias_real, COUNT(*) AS pedidos
FROM   pedidos
WHERE  status <> 'Shipping canceled'
GROUP BY modo, dias_prog, dias_real
ORDER BY modo, dias_real
"""
print('\n=== DISTRIBUIÇÃO prazo x real ===')
print(pd.read_sql(q_dist, con).to_string(index=False))
 
con.close()
