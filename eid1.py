import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy import *
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)

# ── Configuración visual de CustomTkinter ──────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

x = symbols("x")

TRANSFORMATIONS = standard_transformations + (implicit_multiplication_application,)


def parsear_funcion(texto: str):
    """Convierte el texto ingresado por el usuario a una expresión simbólica."""
    texto = texto.strip().replace("^", "**")
    return parse_expr(texto, transformations=TRANSFORMATIONS, local_dict={"x": x, "e": E})


def parsear_h(texto: str):
    """Convierte el texto del valor h a un número simbólico (admite 'inf', '-inf', fracciones)."""
    texto = texto.strip().lower()
    if texto in ("inf", "+inf", "oo", "+oo"):
        return oo
    if texto in ("-inf", "-oo"):
        return -oo
    return sympify(texto)


# ── Aplicación principal ───────────────────────────────────────────────────────
class LimiteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Analizador y Visualizador de Límites — MATE1133")
        self.geometry("1050x680")
        self.resizable(True, True)
        self._construir_ui()

    # ── Construcción de la interfaz ────────────────────────────────────────────
    def _construir_ui(self):
        # Panel izquierdo (controles)
        panel_izq = ctk.CTkFrame(self, width=300, corner_radius=12)
        panel_izq.pack(side="left", fill="y", padx=(16, 8), pady=16)
        panel_izq.pack_propagate(False)

        # Título
        ctk.CTkLabel(
            panel_izq,
            text="Calculadora de Límites",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=(20, 4))
        ctk.CTkLabel(
            panel_izq,
            text="MATE1133 · UCTemuco",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(pady=(0, 20))

        # ── f(x) ──
        ctk.CTkLabel(panel_izq, text="Función  f(x):", anchor="w").pack(
            fill="x", padx=20
        )
        ctk.CTkLabel(
            panel_izq,
            text="Usa x como variable. Ej: (x**2-1)/(x-1)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
            wraplength=240,
        ).pack(fill="x", padx=20, pady=(0, 4))
        self.entrada_fx = ctk.CTkEntry(
            panel_izq, placeholder_text="Ej: sin(x)/x", height=38
        )
        self.entrada_fx.pack(fill="x", padx=20, pady=(0, 16))

        # ── h ──
        ctk.CTkLabel(panel_izq, text="Valor de h  (x → h):", anchor="w").pack(
            fill="x", padx=20
        )
        ctk.CTkLabel(
            panel_izq,
            text="Acepta: números, fracciones, inf, -inf",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 4))
        self.entrada_h = ctk.CTkEntry(
            panel_izq, placeholder_text="Ej: 0  |  2  |  inf", height=38
        )
        self.entrada_h.pack(fill="x", padx=20, pady=(0, 20))

        # ── Botón principal ──
        self.boton = ctk.CTkButton(
            panel_izq,
            text="▶  Calcular y Graficar",
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._calcular,
        )
        self.boton.pack(fill="x", padx=20, pady=(0, 20))

        # ── Separador ──
        ctk.CTkFrame(panel_izq, height=2, fg_color="#3a3a4a").pack(
            fill="x", padx=20, pady=(0, 16)
        )

        # ── Resultado ──
        ctk.CTkLabel(
            panel_izq,
            text="Resultado del límite:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        ).pack(fill="x", padx=20)
        self.lbl_resultado = ctk.CTkLabel(
            panel_izq,
            text="—",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#4fc3f7",
            wraplength=240,
        )
        self.lbl_resultado.pack(pady=(6, 4), padx=20)

        self.lbl_latex = ctk.CTkLabel(
            panel_izq,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=240,
        )
        self.lbl_latex.pack(padx=20)

        # ── Mensajes de error ──
        self.lbl_error = ctk.CTkLabel(
            panel_izq,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#ef9a9a",
            wraplength=240,
        )
        self.lbl_error.pack(padx=20, pady=(8, 0))

        # ── Información del límite ──
        ctk.CTkFrame(panel_izq, height=2, fg_color="#3a3a4a").pack(
            fill="x", padx=20, pady=(16, 8)
        )
        self.lbl_info = ctk.CTkLabel(
            panel_izq,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray70",
            wraplength=240,
            justify="left",
        )
        self.lbl_info.pack(padx=20, fill="x")

        # Panel derecho (gráfica)
        panel_der = ctk.CTkFrame(self, corner_radius=12)
        panel_der.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.fig.patch.set_facecolor("#1e1e2e")
        self._estilo_axes()

        self.canvas = FigureCanvasTkAgg(self.fig, master=panel_der)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self._grafica_vacia()

    # ── Estilo de los ejes ─────────────────────────────────────────────────────
    def _estilo_axes(self):
        self.ax.set_facecolor("#12121e")
        self.ax.tick_params(colors="gray")
        for spine in self.ax.spines.values():
            spine.set_edgecolor("#3a3a4a")
        self.ax.xaxis.label.set_color("gray")
        self.ax.yaxis.label.set_color("gray")
        self.ax.title.set_color("white")

    def _grafica_vacia(self):
        self.ax.clear()
        self._estilo_axes()
        self.ax.set_title("Ingresa una función y presiona Calcular", color="gray")
        self.ax.grid(True, color="#2a2a3a", linestyle="--", linewidth=0.5)
        self.canvas.draw()

    # ── Lógica principal ───────────────────────────────────────────────────────
    def _calcular(self):
        """Se ejecuta SOLO al presionar el botón. Calcula el límite y grafica."""
        self.lbl_error.configure(text="")
        self.lbl_resultado.configure(text="Calculando…", text_color="gray")
        self.lbl_latex.configure(text="")
        self.lbl_info.configure(text="")
        self.update_idletasks()

        try:
            # 1. Parsear entradas
            expr = parsear_funcion(self.entrada_fx.get())
            h_val = parsear_h(self.entrada_h.get())

            # 2. ── CÁLCULO DEL LÍMITE (núcleo matemático) ──────────────────
            #    Se calculan los límites laterales para detectar discontinuidades.
            lim_izq = limit(expr, x, h_val, "-")
            lim_der = limit(expr, x, h_val, "+")

            if lim_izq == lim_der:
                resultado = lim_izq
                tipo = "bilateral"
            else:
                resultado = None
                tipo = "no_existe"

            # 3. Mostrar resultado
            self._mostrar_resultado(expr, h_val, resultado, lim_izq, lim_der, tipo)

            # 4. Graficar
            self._graficar(expr, h_val, resultado)

        except Exception as e:
            self.lbl_resultado.configure(text="Error", text_color="#ef9a9a")
            self.lbl_error.configure(
                text=f"⚠ {str(e)[:120]}\n\nRevisa la sintaxis de la función."
            )

    # ── Presentación del resultado ─────────────────────────────────────────────
    def _mostrar_resultado(self, expr, h_val, resultado, lim_izq, lim_der, tipo):
        h_str = str(h_val)
        expr_str = str(expr)

        if tipo == "bilateral":
            res_str = str(resultado)
            # Intentar forma decimal si es un número finito
            try:
                decimal = float(resultado)
                res_str = f"{resultado}  ≈  {decimal:.6g}"
            except Exception:
                pass
            self.lbl_resultado.configure(text=res_str, text_color="#4fc3f7")
            self.lbl_latex.configure(text=f"lim (x→{h_str})  f(x) = {resultado}")
            self.lbl_info.configure(
                text=f"f(x) = {expr_str}\n\n"
                f"Límite izquierdo: {lim_izq}\n"
                f"Límite derecho:   {lim_der}\n\n"
                "✔ Los límites laterales coinciden."
            )
        else:
            self.lbl_resultado.configure(text="No existe", text_color="#ffb74d")
            self.lbl_latex.configure(text=f"lim (x→{h_str})  f(x) no existe")
            self.lbl_info.configure(
                text=f"f(x) = {expr_str}\n\n"
                f"Límite izquierdo: {lim_izq}\n"
                f"Límite derecho:   {lim_der}\n\n"
                "✘ Los límites laterales son distintos\n"
                "  → el límite bilateral NO existe."
            )

    # ── Graficación ────────────────────────────────────────────────────────────
    def _graficar(self, expr, h_val, resultado):
        self.ax.clear()
        self._estilo_axes()

        # Rango del eje x
        try:
            h_num = float(h_val)
            margen = max(abs(h_num) * 0.5, 4)
            x_ini = h_num - margen
            x_fin = h_num + margen
        except Exception:
            x_ini, x_fin = -10.0, 10.0
            h_num = None

        # Determinar límite numérico para centrar el eje Y
        lim_num = None
        try:
            lim_num = float(resultado)
        except Exception:
            pass

        # Umbral Y: centrado en el límite ± margen, o ±10 si no hay límite finito
        if lim_num is not None:
            margen_y = max(abs(lim_num) * 1.5, 3)
            y_min = lim_num - margen_y
            y_max = lim_num + margen_y
        else:
            y_min, y_max = -10.0, 10.0

        # Generar puntos filtrando todo lo que esté fuera del rango Y visible
        f_lambda = lambdify(x, expr, modules=["sympy"])
        puntos_x = []
        puntos_y = []
        N = 800
        paso = (x_fin - x_ini) / N

        for i in range(N + 1):
            xi = x_ini + i * paso
            try:
                yi = float(f_lambda(xi))
                # Solo graficar puntos dentro del rango Y visible (elimina picos)
                if y_min - abs(y_max - y_min) < yi < y_max + abs(y_max - y_min):
                    puntos_x.append(xi)
                    puntos_y.append(yi)
                else:
                    puntos_x.append(None)
                    puntos_y.append(None)
            except Exception:
                puntos_x.append(None)
                puntos_y.append(None)

        # Dividir en segmentos continuos y graficar
        seg_x, seg_y = [], []
        for px, py in zip(puntos_x, puntos_y):
            if px is None:
                if seg_x:
                    self.ax.plot(seg_x, seg_y, color="#4fc3f7", linewidth=2)
                    seg_x, seg_y = [], []
            else:
                seg_x.append(px)
                seg_y.append(py)
        if seg_x:
            self.ax.plot(seg_x, seg_y, color="#4fc3f7", linewidth=2, label="f(x)")

        # Fijar el eje Y centrado en el límite
        self.ax.set_ylim(y_min, y_max)

        # Marcar el punto h y el límite
        if h_num is not None and lim_num is not None:
            try:
                self.ax.plot(
                    h_num, lim_num,
                    "o", color="#ffb74d", markersize=9,
                    markerfacecolor="#1e1e2e", markeredgewidth=2,
                    zorder=5, label=f"lím = {resultado}",
                )
                self.ax.axvline(h_num, color="#4a4a5a", linestyle=":", linewidth=1)
                self.ax.axhline(lim_num, color="#4a4a5a", linestyle=":", linewidth=1)
            except Exception:
                pass

        self.ax.set_title(f"f(x) = {str(expr)[:60]}", color="white", fontsize=11)
        self.ax.set_xlabel("x", color="gray")
        self.ax.set_ylabel("f(x)", color="gray")
        self.ax.grid(True, color="#2a2a3a", linestyle="--", linewidth=0.5)
        self.ax.legend(
            facecolor="#1e1e2e", edgecolor="#3a3a4a", labelcolor="white", fontsize=10
        )
        self.canvas.draw()


# ── Punto de entrada ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = LimiteApp()
    app.mainloop()