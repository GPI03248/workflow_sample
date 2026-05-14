"""Result output utilities.

Responsibilities:
    - Save solver results to CSV, NPZ, PNG, and Markdown.
    - Handle missing matplotlib gracefully.

Does NOT:
    - Perform any computation.
"""

from __future__ import annotations
import os
import csv
import numpy as np

from ..constants import GAMMA


def save_results(
    output_dir: str,
    U: np.ndarray,
    mesh,
    n_steps: int,
    actual_final_time: float,
    gamma: float = GAMMA,
    case_name: str = "cfd",
    centerline_x: bool = False,
) -> dict:
    """Save CFD results to disk.

    Parameters
    ----------
    output_dir : str
        Directory to write into (created if needed).
    U : np.ndarray, shape (4, nyt, nxt)
        Final conservative variables.
    mesh : StructuredMesh2D
    n_steps : int
    actual_final_time : float
    gamma : float
    case_name : str
        Used in plot titles.
    centerline_x : bool
        If True, also save a centerline density plot (y=mid).

    Returns
    -------
    paths : dict
        Keys: "csv", "npz", "md", and optionally "png" paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    paths = {}
    ng = mesh.ng
    s = (slice(None), slice(ng, -ng), slice(ng, -ng))
    U_int = U[s]
    X, Y = mesh.cell_centers_2d()
    X_int = X[ng:-ng, ng:-ng]
    Y_int = Y[ng:-ng, ng:-ng]

    # Compute primitive.
    rho = U_int[0]
    u = U_int[1] / rho
    v = U_int[2] / rho
    p = (gamma - 1.0) * (U_int[3] - 0.5 * rho * (u**2 + v**2))

    # --- CSV summary ---
    csv_path = os.path.join(output_dir, "summary.csv")
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerow(["case", case_name])
        writer.writerow(["n_steps", n_steps])
        writer.writerow(["actual_final_time", actual_final_time])
        writer.writerow(["rho_min", float(np.min(rho))])
        writer.writerow(["rho_max", float(np.max(rho))])
        writer.writerow(["p_min", float(np.min(p))])
        writer.writerow(["p_max", float(np.max(p))])
        writer.writerow(["u_min", float(np.min(u))])
        writer.writerow(["u_max", float(np.max(u))])
    paths["csv"] = csv_path

    # --- NPZ ---
    npz_path = os.path.join(output_dir, "final_state.npz")
    np.savez(npz_path, U=U_int, X=X_int, Y=Y_int, rho=rho, p=p, u=u, v=v)
    paths["npz"] = npz_path

    # --- Plots (optional) ---
    png_paths = {}
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        # Density.
        fig, ax = plt.subplots(figsize=(8, 5))
        c = ax.pcolormesh(X_int, Y_int, rho, shading="auto")
        fig.colorbar(c, ax=ax, label="rho")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(f"{case_name}: density (t={actual_final_time:.4f})")
        ax.set_aspect("equal")
        fig.tight_layout()
        png_path = os.path.join(output_dir, "density.png")
        fig.savefig(png_path, dpi=150)
        plt.close(fig)
        png_paths["density"] = png_path

        # Pressure.
        fig, ax = plt.subplots(figsize=(8, 5))
        c = ax.pcolormesh(X_int, Y_int, p, shading="auto")
        fig.colorbar(c, ax=ax, label="p")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_title(f"{case_name}: pressure (t={actual_final_time:.4f})")
        ax.set_aspect("equal")
        fig.tight_layout()
        png_path = os.path.join(output_dir, "pressure.png")
        fig.savefig(png_path, dpi=150)
        plt.close(fig)
        png_paths["pressure"] = png_path

        # Centerline density (optional).
        if centerline_x:
            mid_j = rho.shape[0] // 2
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(X_int[mid_j, :], rho[mid_j, :], "b-", linewidth=1.5)
            ax.set_xlabel("x")
            ax.set_ylabel("rho")
            ax.set_title(f"{case_name}: centerline density (y=mid)")
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
            png_path = os.path.join(output_dir, "centerline_density.png")
            fig.savefig(png_path, dpi=150)
            plt.close(fig)
            png_paths["centerline"] = png_path

        paths["png"] = png_paths
    except ImportError:
        paths["png"] = "matplotlib not available"

    # --- Markdown analysis ---
    md_path = os.path.join(output_dir, "analysis.md")
    with open(md_path, "w") as f:
        f.write(f"# {case_name} Analysis\n\n")
        f.write(f"## Simulation Parameters\n\n")
        f.write(f"- nx={mesh.nx}, ny={mesh.ny}\n")
        f.write(f"- dx={mesh.dx:.6f}, dy={mesh.dy:.6f}\n")
        f.write(f"- CFL={mesh.gamma if hasattr(mesh, 'gamma') else 'N/A'}\n")
        f.write(f"- Steps: {n_steps}\n")
        f.write(f"- Actual final time: {actual_final_time:.6f}\n\n")
        f.write(f"## Results\n\n")
        f.write(f"| Quantity | Min | Max |\n")
        f.write(f"|----------|-----|-----|\n")
        f.write(f"| rho | {np.min(rho):.6e} | {np.max(rho):.6e} |\n")
        f.write(f"| u | {np.min(u):.6e} | {np.max(u):.6e} |\n")
        f.write(f"| v | {np.min(v):.6e} | {np.max(v):.6e} |\n")
        f.write(f"| p | {np.min(p):.6e} | {np.max(p):.6e} |\n")
    paths["md"] = md_path

    return paths
