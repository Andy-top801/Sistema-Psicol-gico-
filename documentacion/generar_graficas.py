import os
import matplotlib.pyplot as plt
import numpy as np

# Configurar estilo visual limpio y profesional
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10

output_dir = r'c:\Users\User\Documents\2-2026\SI2\proyecto_grupal\documentacion\imagenes'
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# 1. GRÁFICA BURNDOWN (Sprint 0)
# -------------------------------------------------------------
dias = ['D0\n18/08', 'D1\n19/08', 'D2\n20/08', 'D3\n21/08', 'D4\n22/08', 'D5\n23/08', 'D6\n24/08', 'D7\n24/08 (Fin)']
horas_ideal = [76, 65, 54, 43, 33, 22, 11, 0]
horas_real  = [76, 71, 63, 52, 38, 26, 12, 0]

plt.figure(figsize=(9, 5), dpi=300)
plt.plot(dias, horas_ideal, label='Línea Ideal (Velocidad planificada)', color='#3498db', linestyle='--', linewidth=2.5, marker='o')
plt.plot(dias, horas_real, label='Línea Real (Horas restantes reales)', color='#e74c3c', linewidth=3, marker='s')

# Etiquetas de valores en los puntos
for i, (txt_id, txt_re) in enumerate(zip(horas_ideal, horas_real)):
    plt.annotate(f"{txt_re}h", (dias[i], horas_real[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#c0392b')

plt.title('Gráfica Burndown - Sprint 0 (Horas Restantes: Ideal vs. Real)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Días del Sprint (18 al 24 de agosto de 2026)', fontsize=11, fontweight='bold', labelpad=10)
plt.ylabel('Horas de Trabajo Restantes', fontsize=11, fontweight='bold', labelpad=10)
plt.ylim(-5, 85)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
plt.tight_layout()

burndown_path = os.path.join(output_dir, 'burndown_sprint0.png')
plt.savefig(burndown_path)
plt.close()
print(f"Burndown guardado en: {burndown_path}")

# -------------------------------------------------------------
# 2. GRÁFICA BURNUP (Sprint 0)
# -------------------------------------------------------------
dias_bu = ['D0\n(Inicio)', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7\n(Cierre)']
alcance_total = [18, 18, 18, 18, 18, 18, 18, 18]
tareas_hechas = [0, 1, 3, 6, 9, 12, 15, 18]

plt.figure(figsize=(9, 5), dpi=300)
plt.plot(dias_bu, alcance_total, label='Alcance Total (18 Tareas Planificadas)', color='#8e44ad', linestyle='-', linewidth=2.5)
plt.plot(dias_bu, tareas_hechas, label='Tareas Completadas (Done)', color='#27ae60', linewidth=3, marker='o')

for i, val in enumerate(tareas_hechas):
    plt.annotate(f"{val}", (dias_bu[i], tareas_hechas[i]), textcoords="offset points", xytext=(0,10), ha='center', fontweight='bold', color='#1e8449')

plt.title('Gráfica Burnup - Sprint 0 (Progreso de Tareas vs. Alcance Total)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Días del Sprint 0', fontsize=11, fontweight='bold', labelpad=10)
plt.ylabel('Cantidad de Tareas', fontsize=11, fontweight='bold', labelpad=10)
plt.ylim(-1, 21)
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper left')
plt.tight_layout()

burnup_path = os.path.join(output_dir, 'burnup_sprint0.png')
plt.savefig(burnup_path)
plt.close()
print(f"Burnup guardado en: {burnup_path}")

# -------------------------------------------------------------
# 3. GRÁFICA COMPARATIVA DE ESFUERZO (Horas Estimadas vs. Reales)
# -------------------------------------------------------------
tareas = [f"SP0-{i}" for i in range(1, 19)]
h_est = [4, 2, 2, 5, 1, 3, 5, 6, 3, 8, 2, 5, 2, 4, 8, 4, 8, 4]
h_real = [4, 3, 1, 5, 1, 4, 6, 7, 3, 10, 2, 6, 2, 4, 9, 5, 10, 5]

x = np.arange(len(tareas))
width = 0.38

plt.figure(figsize=(12, 6), dpi=300)
rects1 = plt.bar(x - width/2, h_est, width, label='Horas Estimadas (Total: 76h)', color='#3498db', edgecolor='#2980b9')
rects2 = plt.bar(x + width/2, h_real, width, label='Horas Reales (Total: 87h)', color='#e67e22', edgecolor='#d35400')

plt.title('Comparativa de Esfuerzo por Tarea del Sprint 0 (Horas Estimadas vs. Horas Reales)', fontsize=13, fontweight='bold', pad=15)
plt.xlabel('Código de Tarea (Sprint Backlog)', fontsize=11, fontweight='bold', labelpad=10)
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

esfuerzo_path = os.path.join(output_dir, 'esfuerzo_sprint0.png')
plt.savefig(esfuerzo_path)
plt.close()
print(f"Esfuerzo guardado en: {esfuerzo_path}")
