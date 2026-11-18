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


def cargar_datos_gx339(ruta_csv=None):
    # Carga datos observacionales de RXTE para GX 339-4
    if ruta_csv is None:
        ruta_csv = os.path.join(DATOS_DIR, "gx339_rxte_2002_belloni.csv")
    df = pd.read_csv(ruta_csv)
    return df


def generar_diagrama_hid(df=None, ruta_salida=None):
    # Genera el diagrama dureza-intensidad con histeresis
    if df is None:
        df = cargar_datos_gx339()
    if ruta_salida is None:
        ruta_salida = os.path.join(DIAG_DIR, "hid_gx339_4.png")

    fig, ax = plt.subplots(figsize=(10, 7), dpi=300)

    # Mapeo de colores y nombres de estados en espanol
    colores_estado = {
        "LHS": ("#1f77b4", "Estado Bajo/Duro (LHS)"),
        "HIMS": ("#ff7f0e", "Estado Intermedio Duro (HIMS)"),
        "SIMS": ("#9467bd", "Estado Intermedio Blando (SIMS)"),
        "HSS": ("#d62728", "Estado Alto/Blando (HSS)"),
    }

    # Trayectoria temporal
    hr = df["hr"].values
    tasa = df["pcu2_rate"].values
    ax.plot(hr, tasa, color="#95a5a6", lw=1.2, alpha=0.6, zorder=1)

    # Puntos por estado
    for st, (col, etiqueta) in colores_estado.items():
        sub = df[df["state"] == st]
        ax.scatter(
            sub["hr"],
            sub["pcu2_rate"],
            c=col,
            label=f"{etiqueta} (N={len(sub)})",
            s=45,
            edgecolor="black",
            linewidth=0.5,
            alpha=0.9,
            zorder=3,
        )

    # Linea de chorro (Jet Line)
    ax.axvline(
        x=0.25,
        color="#c0392b",
        linestyle="--",
        lw=1.8,
        label="Linea de Chorro (Transicion HIMS/SIMS)",
        zorder=2,
    )

    # Anotaciones
    ax.text(
        0.76,
        250,
        "Subida en Estado Duro\n(Chorro continuo activo)",
        fontsize=9,
        fontweight="bold",
        color="#1f77b4",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="#ebf5fb", ec="#1f77b4", lw=0.8),
    )
    ax.text(
        0.55,
        1300,
        "Transicion Superior\n(Aceleracion de chorro)",
        fontsize=9,
        fontweight="bold",
        color="#d35400",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="#fef5e7", ec="#d35400", lw=0.8),
    )
    ax.text(
        0.25,
        1400,
        "Linea de Chorro:\nEyecciones balisticas relativistas",
        fontsize=8.5,
        fontweight="bold",
        color="#c0392b",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="#fadbd8", ec="#c0392b", lw=0.8),
    )
    ax.text(
        0.2,
        120,
        "Estado Blando\n(Disco en ISCO,\n chorro apagado)",
        fontsize=9,
        fontweight="bold",
        color="#c0392b",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="#fdedec", ec="#c0392b", lw=0.8),
    )
    ax.text(
        0.55,
        100,
        "Retorno y Transicion Inferior\n(Histeresis. Factor: ~15 menos)",
        fontsize=9,
        fontweight="bold",
        color="#d35400",
        ha="center",
        bbox=dict(boxstyle="round,pad=0.3", fc="#fef5e7", ec="#d35400", lw=0.8),
    )

    ax.set_yscale("log")
    ax.set_xlim(0.04, 0.98)
    ax.set_ylim(6.0, 2000.0)
    ax.set_xlabel("Dureza", fontsize=11, fontweight="bold")
    ax.set_ylabel("Tasa cuentas PCU2 [cuentas s⁻¹]", fontsize=11, fontweight="bold")
    ax.set_title(
        "Diagrama Dureza-Intensidad (HID) de GX 339-4",
        fontsize=12,
        fontweight="bold",
        pad=12,
    )
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend(loc="lower left", fontsize=8.5, framealpha=0.95)

    fig.tight_layout()
    fig.savefig(ruta_salida, dpi=300)
    plt.close(fig)
    return ruta_salida



def ejecutar():
    print("Generando diagramas HID...\n")
    print("[1/2] Carga de datos...")
    df = cargar_datos_gx339()
    print(" Completado.\n")
    print("[2/2] Generación HID...")
    r1 = generar_diagrama_hid(df)
    print(" Completado.\n")
    return r1


if __name__ == "__main__":
    ejecutar()
