import pandas as pd
import matplotlib.pyplot as plt

# Parâmetros da carta de controle
padrao = 0.1  # mg/L
limite_superior = padrao * 1.10
limite_inferior = padrao * 0.90

# Dados de exemplo
dados = {
    'Data': ['2025-01-01', '2025-01-05', '2025-01-10', '2025-01-15', '2025-01-20'],
    'Resultado': [0.098, 0.102, 0.105, 0.091, 0.087]
}

df = pd.DataFrame(dados)
df['Data'] = pd.to_datetime(df['Data'])

# Gráfico
plt.figure(figsize=(10, 5))
plt.plot(df['Data'], df['Resultado'], marker='o', linestyle='-', color='blue', label='Resultados')
plt.axhline(padrao, color='green', linestyle='--', label='Padrão (0,1 mg/L)')
plt.axhline(limite_superior, color='red', linestyle='--', label='Limite Superior (+10%)')
plt.axhline(limite_inferior, color='red', linestyle='--', label='Limite Inferior (-10%)')
plt.fill_between(df['Data'], limite_inferior, limite_superior, color='red', alpha=0.1)

plt.title('Carta de Controle de Ensaios')
plt.xlabel('Data')
plt.ylabel('Resultado (mg/L)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
