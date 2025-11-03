# IEC_modelsim.py - Implementación teórica de rho_v = E / V_total

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

# ======================
# PARÁMETRES COSMOLÓGICOS
# ======================
H0 = 1.0
rho_m0_target = 0.30
a_recomb = 1e-3
t_recomb = 1e-6
t_today = 1.0
t_max = 1.5

# --- CALIBRACIÓN FINAL ---
V_m_total = 6.0                  # Volumen total de materia
eta = 0.90                       # Eficiencia de acoplamiento P -> E
k_elastic = 1.0                  # Factor de elasticidad (P_v = -k_elastic * E)
beta = 0.025                     # Tasa de formación de vacíos por colapso
gamma = 3.2                      # Tasa de expansión elástica

# Tiempos
t = np.logspace(-12, np.log10(t_max), 35000)
key_times = [1e-10, 1e-8, t_recomb, 1e-4, 0.1, t_today]

# ======================
# MODELO FINAL (Ecuaciones de Friedmann y Evolución de Variables)
# ======================
def model(y, t):
    a, V_v, E = y
    V_m = V_m_total
    V_total = V_m + V_v
    if V_total < 1e-50: V_total = 1e-50
    
    # 1. Densidad de materia
    rho_m = rho_m0_target * (a_recomb / a)**3
    
    # 2. Presión positiva temprana
    P_pos = 850.0 * (t_recomb / t)**1.7 if t < t_recomb else 0.0
    
    # 3. Evolución de la Elasticidad (E)
    dE_dt = eta * P_pos * (1 - V_v / V_total) if t < t_recomb else 0.0
    
    # 4. Presión negativa (Ecuación de estado w = -1)
    P_v = -k_elastic * E
    
    # 5. Evolución del Volumen de Vacíos (V_v)
    dV_v_dt = beta * rho_m * V_m + gamma * E * (1 - V_v / V_total)**1.8
    dV_v_dt = max(dV_v_dt, 0)
    
    # 6. Densidad de Vacíos (¡CLAVE!)
    # Basado en la teoría CEI: rho_v = E / V_total
    rho_v = E / V_total
    
    # 7. Ecuación de Friedmann (H²)
    H2 = rho_m + rho_v
    H = np.sqrt(max(H2, 1e-20))
    
    da_dt = a * H
    return [da_dt, dV_v_dt, dE_dt]

# ======================
# Integración
# ======================
y0 = [a_recomb, 1e-60, 0.0]
sol = odeint(model, y0, t, rtol=1e-10, atol=1e-15)
a, V_v, E = sol.T
V_m = np.full_like(t, V_m_total)
V_total = V_m + V_v

# ======================
# Normalización (a(t_today) = 1)
# ======================
idx_today = np.abs(t - t_today).argmin()
a_norm = a / a[idx_today]
V_total_norm = V_m + V_v
omega_m = V_m / V_total_norm
omega_v = V_v / V_total_norm

# ======================
# Cálculos finales (para resultados y gráficas)
# ======================
rho_m = rho_m0_target * (a_recomb / a_norm)**3
# Aplicamos la corrección teórica también en la salida:
rho_v = E / V_total_norm 

P_v = -k_elastic * E
P_pos = np.where(t < t_recomb, 850.0 * (t_recomb / t)**1.7, 0.0)
ddota = -(rho_m + 3*P_pos) - (rho_v + 3*P_v) # Ecuación de aceleración

# ======================
# SALIDA
# ======================
print("--- Resultados del Modelo CEI (Corregido) ---")
print(f"\\Omega_m = {omega_m[idx_today]:.3f}")
print(f"\\Omega_v = {omega_v[idx_today]:.3f}")

# ======================
# GRÁFICAS PARA EL ANEXO
# ======================
plt.figure(figsize=(12, 8))

plt.subplot(2, 2, 1)
plt.plot(t, a_norm, 'b-')
plt.xscale('log')
plt.xlabel('Tiempo (unidades $H_0^{-1}$)')
plt.ylabel('Factor de escala $a(t)$')
plt.title('Expansión Cósmica')
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 2)
plt.plot(t, V_v, 'g-')
plt.xscale('log')
plt.xlabel('Tiempo')
plt.ylabel('Volumen de vacíos $V_v(t)$')
plt.title('Crecimiento de Vacíos')
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 3)
plt.plot(t, E, 'r-')
plt.xscale('log')
plt.xlabel('Tiempo')
plt.ylabel('Elasticidad $E(t)$')
plt.axvline(t_recomb, color='k', ls='--', label='$t_{\\text{recomb}}$')
plt.legend()
plt.title('Memoria Elástica')
plt.grid(True, alpha=0.3)

plt.subplot(2, 2, 4)
plt.plot(t, omega_m, label=r'$\Omega_m(t)$', color='purple')
plt.plot(t, omega_v, label=r'$\Omega_v(t)$', color='orange')
plt.xscale('log')
plt.xlabel('Tiempo')
plt.ylabel('Densidad relativa')
plt.legend()
plt.title(r'Evolución de $\Omega$')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('cei_simulation.pdf', dpi=300, bbox_inches='tight')
plt.close()

print("¡GRÁFICA GUARDADA: cei_simulation.pdf!")