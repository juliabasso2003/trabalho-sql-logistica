from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

CAMINHO = r'C:\Users\lucas\OneDrive\Área de Trabalho\trabalho-sql-logistica\data\DataCoSupplyChainDataset.csv'
PASTA_GRAFICOS = Path(__file__).resolve().parent.parent / 'output'
PASTA_GRAFICOS.mkdir(parents=True, exist_ok=True)

colunas = [
    'Shipping Mode',
    'Delivery Status',
    'Late_delivery_risk',
    'Days for shipping (real)',
    'Days for shipment (scheduled)',
    'Customer City',
]
df = pd.read_csv(CAMINHO, encoding='latin1', usecols=colunas)

df = df.rename(columns={
    'Shipping Mode': 'modo',
    'Delivery Status': 'status',
    'Late_delivery_risk': 'risco_atraso',
    'Days for shipping (real)': 'dias_real',
    'Days for shipment (scheduled)': 'dias_prog',
    'Customer City': 'city',
})

# WHERE: remove pedidos cancelados
#    SQL: WHERE status <> 'Shipping canceled'
d = df[df['status'] != 'Shipping canceled'].copy()

# Colunas calculadas (equivalem aos CASE WHEN / expressões do SELECT)
d['atrasado'] = (d['status'] == 'Late delivery').astype(int)   # 1 = atrasado, 0 = não
d['diferenca'] = d['dias_real'] - d['dias_prog']               # positivo = demorou mais que o prometido
d['acima_prazo'] = (d['dias_real'] > d['dias_prog']).astype(int)

# PERGUNTA: qual Shipping Mode tem a maior taxa de atraso?
q3 = (
    d.groupby('modo')
    .agg(
        total_pedidos=('atrasado', 'size'),   # COUNT(*)
        atrasados=('atrasado', 'sum'),        # SUM(CASE WHEN ...)
    )
    .reset_index()
)
q3['taxa_atraso_pct'] = (q3['atrasados'] / q3['total_pedidos'] * 100).round(1)
q3 = q3.sort_values('taxa_atraso_pct', ascending=False)   # ORDER BY ... DESC

print('=== PERGUNTA 3: taxa de atraso por modo ===')
print(q3.to_string(index=False))

# PERGUNTA: o prazo programado é realista?
#    diferença = dias_real - dias_prog  (positivo = demorou mais que o prometido)
q4 = (
    d.groupby('modo')
    .agg(
        prazo_prog_medio=('dias_prog', 'mean'),     # AVG
        prazo_real_medio=('dias_real', 'mean'),
        diferenca_media=('diferenca', 'mean'),
        menor_diferenca=('diferenca', 'min'),       # MIN
        maior_diferenca=('diferenca', 'max'),       # MAX
        pct_acima_do_prazo=('acima_prazo', 'mean'),
    )
    .reset_index()
)
q4['pct_acima_do_prazo'] = (q4['pct_acima_do_prazo'] * 100).round(1)
q4[['prazo_prog_medio', 'prazo_real_medio', 'diferenca_media']] = (
    q4[['prazo_prog_medio', 'prazo_real_medio', 'diferenca_media']].round(2)
)
q4 = q4.sort_values('diferenca_media', ascending=False)

print('\n=== PERGUNTA 4: prazo programado x real ===')
print(q4.to_string(index=False))

# "O real fica SEMPRE acima do programado?" -> menor_diferenca > 0 em algum modo?

# JOIN: junta as duas análises pela coluna 'modo'
resumo = (
    q3[['modo', 'total_pedidos', 'taxa_atraso_pct']]
    .merge(
        q4[['modo', 'prazo_prog_medio', 'prazo_real_medio',
            'diferenca_media', 'menor_diferenca']],
        on='modo',
        how='inner',
    )
    .sort_values('taxa_atraso_pct', ascending=False)
)

print('\n=== RESUMO (JOIN) ===')
print(resumo.to_string(index=False))

# Distribuição: quantos pedidos por combinação prazo x real
dist = (
    d.groupby(['modo', 'dias_prog', 'dias_real'])
    .size()
    .reset_index(name='pedidos')
    .sort_values(['modo', 'dias_real'])
)

print('\n=== DISTRIBUIÇÃO prazo x real ===')
print(dist.to_string(index=False))

# PERGUNTA: quais são os 10 países com maior tempo médio de entrega?
q5 = (
    d.groupby('city')
    .agg(
        tempo_medio_entrega_dias=('dias_real', 'mean'),
        total_pedidos=('dias_real', 'size'),
    )
    .reset_index()
    .sort_values('tempo_medio_entrega_dias', ascending=False)
    .head(10)
)
q5['tempo_medio_entrega_dias'] = q5['tempo_medio_entrega_dias'].round(2)

print('\n=== PERGUNTA 5: 10 países com maior tempo médio de entrega ===')
print(q5.to_string(index=False))

# Salva os gráficos gerados na pasta outputs
plt.figure(figsize=(8, 5))
plt.bar(q3['modo'], q3['taxa_atraso_pct'], color='steelblue')
plt.title('Taxa de atraso por modo de envio')
plt.xlabel('Modo de envio')
plt.ylabel('Taxa de atraso (%)')
plt.xticks(rotation=20, ha='right')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / 'taxa_atraso_por_modo.png', dpi=150)
plt.close()

plt.figure(figsize=(8, 5))
plt.plot(q4['modo'], q4['prazo_prog_medio'], marker='o', label='Prazo programado')
plt.plot(q4['modo'], q4['prazo_real_medio'], marker='o', label='Prazo real')
plt.title('Prazo médio programado x real por modo de envio')
plt.xlabel('Modo de envio')
plt.ylabel('Dias')
plt.xticks(rotation=20, ha='right')
plt.legend()
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / 'prazo_programado_vs_real.png', dpi=150)
plt.close()

plt.figure(figsize=(9, 6))
plt.barh(
    q5['city'].iloc[::-1],
    q5['tempo_medio_entrega_dias'].iloc[::-1],
    color='darkorange',
)
plt.title('10 cidades com maior tempo médio de entrega')
plt.xlabel('Tempo médio de entrega (dias)')
plt.ylabel('city')
plt.tight_layout()
plt.savefig(PASTA_GRAFICOS / 'top_10_cidades_tempo_medio_entrega.png', dpi=150)
plt.close()

print(f'\nGráficos salvos em: {PASTA_GRAFICOS}')