import os
os.environ["MPLCONFIGDIR"] = "/tmp/mpl_cache"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Directorios de trabajo base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATOS_DIR = os.path.join(BASE_DIR, "codigo", "datos")
DIAG_DIR = os.path.join(BASE_DIR, "Figuras/Experimentos numéricos")

# Constantes fisicas
C_MS = 299792458.0
MAS_DIA_A_RAD_S = (1e-3 / 3600.0) * (np.pi / 180.0) / 86400.0
KPC_A_M = 3.08567758149137e19
FACTOR_CONVERSION = MAS_DIA_A_RAD_S * KPC_A_M / C_MS


def velocidad_aparente(beta, theta_rad, recesivo=False):
    # Calcula la velocidad transversal aparente beta_ap = v_ap / c
    if recesivo:
        return (beta * np.sin(theta_rad)) / (1.0 + beta * np.cos(theta_rad))
    return (beta * np.sin(theta_rad)) / (1.0 - beta * np.cos(theta_rad))


def calcular_angulo_maxima_velocidad(beta):
    # Calcula el angulo y la velocidad aparente maxima beta * Gamma
    gamma = 1.0 / np.sqrt(1.0 - beta**2)
    theta_max_rad = np.arccos(beta)
    beta_app_max = beta * gamma
    return theta_max_rad, beta_app_max


def calcular_parametros_cinematicos(mu_a, mu_r, d_kpc):
    # Invierte los parametros fisicos beta, theta y Gamma a partir de mu_a, mu_r y distancia D
    beta_cos = (mu_a - mu_r) / (mu_a + mu_r)
    d_max = 1.0 / (FACTOR_CONVERSION * np.sqrt(mu_a * mu_r))
    tan_theta = (2.0 * d_kpc * FACTOR_CONVERSION * mu_a * mu_r) / (mu_a - mu_r)
    theta_rad = np.arctan(tan_theta)
    beta_sin = (2.0 * d_kpc * FACTOR_CONVERSION * mu_a * mu_r) / (mu_a + mu_r)
    beta = np.sqrt(beta_cos**2 + beta_sin**2)
    gamma = 1.0 / np.sqrt(max(1e-9, 1.0 - beta**2))
    beta_app_a = velocidad_aparente(beta, theta_rad, recesivo=False)
    beta_app_r = velocidad_aparente(beta, theta_rad, recesivo=True)
    return {
        "beta_cos": beta_cos,
        "d_max_kpc": d_max,
        "theta_deg": np.degrees(theta_rad),
        "beta": beta,
        "gamma": gamma,
        "beta_app_a": beta_app_a,
        "beta_app_r": beta_app_r,
    }


def razon_flujo_doppler(mu_a, mu_r, k=3, alpha=-0.7):
    # Calcula la razon de densidades de flujo relativista S_a / S_r
    return (mu_a / mu_r) ** (k - alpha)



def generar_diagrama_velocidad_superluminica(ruta_salida=None):
    # Grafica velocidad transversal aparente beta_ap vs angulo de inclinacion theta
    if ruta_salida is None:
        ruta_salida = os.path.join(DIAG_DIR, "velocidad_superluminica.png")

    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)

    theta_deg = np.linspace(0.1, 90.0, 500)
    theta_rad = np.radians(theta_deg)

    betas = [0.50, 0.7071, 0.80, 0.885, 0.92, 0.95, 0.98]
    colores = plt.cm.plasma(np.linspace(0.1, 0.95, len(betas)))

    # Curvas teoricas aproximantes
    for b, col in zip(betas, colores):
        beta_app = velocidad_aparente(b, theta_rad, recesivo=False)
        lbl = f"$\\beta = {b:.3f}$" if b == 0.7071 else f"$\\beta = {b:.2f}$"
        ax.plot(theta_deg, beta_app, color=col, lw=1.8, label=lbl)

    # Curva envolvente de maximos
    beta_vals = np.linspace(0.01, 0.99, 300)
    theta_max_deg = np.degrees(np.arccos(beta_vals))
    beta_max_app = beta_vals / np.sqrt(1.0 - beta_vals**2)
    ax.plot(theta_max_deg, beta_max_app, color="#2c3e50", ls="--", lw=1.6, label="$v_{{max}}$ ($\\beta_{{ap,max}} = \\beta\\Gamma$)")

    # Limite superlumínico
    ax.axhline(1.0, color="#c0392b", ls="-.", lw=1.5, label="Limite lumínico ($v_{ap} = c$)")
    ax.fill_between(theta_deg, 1.0, 5.0, color="#e74c3c", alpha=0.08, label="Superlumínico aparente ($\\beta_{ap} > 1$)")

    # Microcuasares observados
    microcuasares = [
        ("GRS 1915+105", 69.4, 1.27, "#ff0000", "GRS 1915+105\n$\\beta\\approx 0.92, \\theta=69.4^\\circ$\n$\\beta_{ap}=1.27$"),
        ("MAXI J1820+070", 63.1, 1.32, "#13a313", "MAXI J1820+070\n$\\beta\\approx 0.89, \\theta=63.1^\\circ$\n$\\beta_{ap}=1.32$"),
        ("GRO J1655-40", 85.0, 1.05, "#0000ff", "GRO J1655-40\n$\\beta\\approx 0.92, \\theta=85.0^\\circ$\n$\\beta_{ap}=1.05$"),
    ]

    for idx, [nom, th, b_app, col, texto] in enumerate(microcuasares):
        ax.scatter([th], [b_app], color=col, s=90, zorder=6, edgecolor="black", lw=1.0)
        ax.text(
            th - 6*int(idx==1) - 8*int(idx==2),
            b_app + 0.15 - 0.55*int(idx==2),
            texto,
            fontsize=8.5,
            fontweight="bold",
            color=col,
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=col, lw=0.9),
        )

    
    ax.set_xlim(0, 90)
    ax.set_ylim(0, 3.8)
    ax.set_xlabel("Ángulo de inclinacion wrt línea de visión (grados)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Velocidad transversal aparente $\\beta_{ap} = v_{ap} / c$", fontsize=11, fontweight="bold")
    ax.set_title(
        "Velocidad Transversal Aparente ($\\beta_{ap}$), movimiento superlumínico\n",
        fontsize=12,
        fontweight="bold",
        pad=10,
    )
    ax.grid(True, ls=":", alpha=0.6)
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.95)

    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=300)
    plt.close(fig)
    return ruta_salida


def ejecutar():
    print("[1/1] Generando diagrama velocidad superlumínica...")
    r1 = generar_diagrama_velocidad_superluminica()
    print(" Completado.\n")
    return r1


if __name__ == "__main__":
    ejecutar()
