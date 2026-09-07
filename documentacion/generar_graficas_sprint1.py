import os
import matplotlib.pyplot as plt
import numpy as np

# Configurar estilo visual limpio y profesional
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

output_dir = r'c:\Users\User\Documents\2-2026\SI2\PROYECTO_GRUPAL_OFI\documentacion\imagenes'
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. GRÁFICA BURNDOWN (Sprint 1: 26/08 al 06/09 - 12 días, 73 horas)
# -------------------------------------------------------------
dias = [
    'D0\n26/08', 'D1\n27/08', 'D2\n28/08', 'D3\n29/08', 'D4\n30/08', 'D5\n31/08',
    'D6\n01/09', 'D7\n02/09', 'D8\n03/09', 'D9\n04/09', 'D10\n05/09', 'D11\n06/09', 'D12\nFin'
]
# Total 73 horas estimadas
horas_ideal = [73, 67, 61, 55, 49, 43, 37, 30, 24, 18, 12, 6, 0]
horas_real  = [73, 69, 64, 58, 52, 45, 38, 29, 21, 14, 8, 3, 0]

plt.figure(figsize=(11, 5.5), dpi=300)
plt.plot(dias, horas_ideal, label='Línea Ideal (Velocidad planificada: ~6.1h/día)', color='#3498db', linestyle='--', linewidth=2.5, marker='o')
plt.plot(dias, horas_real, label='Línea Real (Horas restantes reales)', color='#e74c3c', linewidth=3, marker='s')

for i, (txt_id, txt_re) in enumerate(zip(horas_ideal, horas_real)):
    plt.annotate(f"{txt_re}h", (dias[i], horas_real[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#c0392b', fontsize=8.5)

plt.title('Gráfica Burndown - Sprint 1 (Horas Restantes: Ideal vs. Real)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Días del Sprint 1 (26 de agosto al 06 de septiembre de 2026)', fontsize=11, fontweight='bold', labelpad=10)
plt.ylabel('Horas de Trabajo Restantes', fontsize=11, fontweight='bold', labelpad=10)
plt.ylim(-5, 85)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
plt.tight_layout()

burndown_path = os.path.join(output_dir, 'burndown_sprint1.png')
plt.savefig(burndown_path)
plt.close()
print(f"Burndown guardado en: {burndown_path}")

# -------------------------------------------------------------
# 2. GRÁFICA BURNUP (Sprint 1: 15 Tareas Planificadas, Nro 19 al 33)
# -------------------------------------------------------------
dias_bu = ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12']
alcance_total = [15] * 13
tareas_hechas = [0, 1, 2, 3, 5, 7, 8, 10, 11, 13, 14, 15, 15]

plt.figure(figsize=(11, 5.5), dpi=300)
plt.plot(dias_bu, alcance_total, label='Alcance Total (15 Tareas Planificadas: SP1-19 a SP1-33)', color='#8e44ad', linestyle='-', linewidth=2.5)
plt.plot(dias_bu, tareas_hechas, label='Tareas Completadas (Done)', color='#27ae60', linewidth=3, marker='o')

for i, val in enumerate(tareas_hechas):
    plt.annotate(f"{val}", (dias_bu[i], tareas_hechas[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#1e8449', fontsize=8.5)

plt.title('Gráfica Burnup - Sprint 1 (Progreso de Tareas vs. Alcance Total)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Días del Sprint 1 (26 de agosto al 06 de septiembre de 2026)', fontsize=11, fontweight='bold', labelpad=10)
plt.ylabel('Cantidad de Tareas Terminadas', fontsize=11, fontweight='bold', labelpad=10)
plt.ylim(-1, 18)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
plt.tight_layout()

burnup_path = os.path.join(output_dir, 'burnup_sprint1.png')
plt.savefig(burnup_path)
plt.close()
print(f"Burnup guardado en: {burnup_path}")

# -------------------------------------------------------------
# 3. GRÁFICA COMPARATIVA DE ESFUERZO (15 Tareas: SP1-19 a SP1-33)
# -------------------------------------------------------------
tareas = [f"SP1-{i}" for i in range(19, 34)]
h_est = [4, 8, 3, 4, 8, 3, 4, 8, 3, 4, 8, 3, 3, 7, 3] # Total 73h
h_real = [4, 10, 3, 4, 9, 3, 4, 9, 3, 4, 10, 3, 3, 8, 3] # Total 80h (+7h)

x = np.arange(len(tareas))
width = 0.38

plt.figure(figsize=(13, 6), dpi=300)
rects1 = plt.bar(x - width/2, h_est, width, label='Horas Estimadas (Total: 73h)', color='#3498db', edgecolor='#2980b9')
rects2 = plt.bar(x + width/2, h_real, width, label='Horas Reales (Total: 80h)', color='#e67e22', edgecolor='#d35400')

plt.title('Comparativa de Esfuerzo por Tarea del Sprint 1 (Horas Estimadas vs. Horas Reales)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Código de Tarea (Sprint Backlog: SP1-19 a SP1-33)', fontsize=11, fontweight='bold', labelpad=10)
plt.ylabel('Horas Invertidas', fontsize=11, fontweight='bold', labelpad=10)
plt.xticks(x, tareas, rotation=45)
plt.ylim(0, 13)
plt.grid(True, linestyle=':', alpha=0.6, axis='y')
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')

# Añadir valores sobre las barras
for rect in rects1:
    h = rect.get_height()
    plt.annotate(f'{h}', (rect.get_x() + rect.get_width()/2, h), textcoords="offset points", xytext=(0,3), ha='center', fontsize=8, color='#2c3e50')
for rect in rects2:
    h = rect.get_height()
    plt.annotate(f'{h}', (rect.get_x() + rect.get_width()/2, h), textcoords="offset points", xytext=(0,3), ha='center', fontsize=8, fontweight='bold', color='#ba4a00')

plt.tight_layout()

esfuerzo_path = os.path.join(output_dir, 'esfuerzo_sprint1.png')
plt.savefig(esfuerzo_path)
plt.close()
print(f"Esfuerzo guardado en: {esfuerzo_path}")
