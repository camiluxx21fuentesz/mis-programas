import tkinter as tk
from tkinter import ttk, messagebox


class VentanaBienvenida(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bienvenida a La Heladeria")
        self.resizable(False, False)
        self.configure(bg="#FFB6C1")

        self.bienvenida = tk.Frame(self, bg="#FFB6C1", padx=30, pady=25)
        self.bienvenida.pack()

        tk.Label(
            self.bienvenida,
            text="La Heladeria",
            bg="#FFB6C1",
            fg="#FFD700",
            font=("Segoe UI", 30, "bold"),
        ).pack()

        tk.Label(
            self.bienvenida,
            text="Los mejores sabores de la ciudad",
            bg="#FFB6C1",
            fg="#800080",
            font=("Segoe UI", 11),
        ).pack(pady=(4, 18))

        boton_entrar = tk.Button(
            self.bienvenida,
            text="Entrar",
            bg="#FFD700",
            fg="#8B0050",
            activebackground="#E6C200",
            activeforeground="#8B0050",
            font=("Segoe UI", 14, "bold"),
            relief="flat",
            bd=0,
            padx=40,
            pady=8,
            cursor="hand2",
            command=self.abrir_sistema,
        )
        boton_entrar.pack()
        boton_entrar.bind("<Enter>", lambda e: boton_entrar.config(bg="#E6C200"))
        boton_entrar.bind("<Leave>", lambda e: boton_entrar.config(bg="#FFD700"))

        self.ventana_sistema = None

    def abrir_sistema(self):
        self.ventana_sistema = VentanaPrincipal()
        self.ventana_sistema.show()
        self.withdraw()


class VentanaPrincipal(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("La Heladeria - Sistema de Pedidos")
        self.resizable(False, False)
        self.configure(bg="#FFD700")

        self.contenedor = tk.Frame(self, bg="#FFD700", padx=22, pady=16)
        self.contenedor.pack(fill="both", expand=True)

        tk.Label(
            self.contenedor,
            text="La Heladeria",
            bg="#FFD700",
            fg="#800080",
            font=("Segoe UI", 22, "bold"),
        ).pack(pady=(0, 14))

        self.campo_nombre = self._crear_entrada("Nombre del cliente:", "Escribe tu nombre...")
        self.combo_sabor = self._crear_combo(
            "Sabor del helado:",
            ["Vainilla", "Chocolate", "Fresa", "Menta", "Dulce de leche", "Frutilla"],
        )
        self.combo_topping = self._crear_combo(
            "Topping extra:",
            ["Ninguno", "Salsa de chocolate", "Salsa de fresa", "Chispas de colores", "Oreo", "Cerezas"],
        )
        self.campo_cantidad = self._crear_entrada("Cantidad:", "1")

        tk.Label(
            self.contenedor,
            text="Opciones extra:",
            bg="#FFD700",
            fg="#333333",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(12, 4))

        self.radio_cucurucho, self.radio_cono, self.radio_nieve = self._crear_radios()

        self.var_llevar = tk.IntVar(value=0)
        self.check_llevar = tk.Checkbutton(
            self.contenedor,
            text="Pedido para llevar",
            variable=self.var_llevar,
            bg="#FFD700",
            fg="#333333",
            activebackground="#FFD700",
            activeforeground="#333333",
            selectcolor="#FFD700",
            font=("Segoe UI", 10),
            anchor="w",
        )
        self.check_llevar.pack(fill="x", pady=(2, 0))

        tk.Label(
            self.contenedor,
            text="Observaciones:",
            bg="#FFD700",
            fg="#333333",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x", pady=(12, 4))

        self.texto_obs = tk.Text(
            self.contenedor,
            height=3,
            wrap="word",
            bg="white",
            fg="#333333",
            relief="flat",
            font=("Segoe UI", 10),
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        self.texto_obs.pack(fill="x")
        self.texto_obs._placeholder = (
            "Escribe alergias, preferencias o instrucciones especiales..."
        )
        self.texto_obs.insert("1.0", self.texto_obs._placeholder)
        self.texto_obs.config(fg="#999999")
        self.texto_obs.bind("<FocusIn>", self._quitar_placeholder)
        self.texto_obs.bind("<FocusOut>", self._restaurar_placeholder)

        marco_botones = tk.Frame(self.contenedor, bg="#FFD700")
        marco_botones.pack(fill="x", pady=(16, 0))

        self.boton_confirmar = self._crear_boton(
            marco_botones, "Confirmar Pedido", "#FF69B4", self.confirmar_pedido
        )
        self.boton_limpiar = self._crear_boton(
            marco_botones, "Limpiar", "#800080", self.limpiar
        )

        self.resultado = tk.Label(
            self.contenedor,
            text="",
            bg="#FFB6C1",
            fg="#800080",
            font=("Segoe UI", 11, "bold"),
            wraplength=460,
            padx=10,
            pady=10,
        )
        self.resultado.pack(fill="x", pady=(14, 0))

        tk.Label(
            self.contenedor,
            text="Creado por Camila Marcela",
            bg="#FFD700",
            fg="#800080",
            font=("Segoe UI", 8, "italic"),
        ).pack(pady=(6, 0))

        self.protocol("WM_DELETE_WINDOW", self.cerrar)

    def show(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _crear_entrada(self, etiqueta, placeholder):
        fila = tk.Frame(self.contenedor, bg="#FFD700")
        fila.pack(fill="x", pady=4)
        tk.Label(
            fila,
            text=etiqueta,
            bg="#FFD700",
            fg="#333333",
            font=("Segoe UI", 10, "bold"),
            width=16,
            anchor="w",
        ).pack(side="left")

        entry = tk.Entry(
            fila,
            bg="white",
            fg="#333333",
            relief="flat",
            font=("Segoe UI", 10),
            highlightthickness=1,
            highlightbackground="#cccccc",
        )
        entry.pack(side="left", fill="x", expand=True, ipady=5)
        entry._placeholder = placeholder
        entry.insert(0, placeholder)
        entry.config(fg="#999999")
        entry.bind("<FocusIn>", self._quitar_placeholder)
        entry.bind("<FocusOut>", self._restaurar_placeholder)
        return entry

    def _crear_combo(self, etiqueta, valores):
        fila = tk.Frame(self.contenedor, bg="#FFD700")
        fila.pack(fill="x", pady=4)
        tk.Label(
            fila,
            text=etiqueta,
            bg="#FFD700",
            fg="#333333",
            font=("Segoe UI", 10, "bold"),
            width=16,
            anchor="w",
        ).pack(side="left")

        combo = ttk.Combobox(fila, values=valores, state="readonly", font=("Segoe UI", 10))
        combo.current(0)
        combo.pack(side="left", fill="x", expand=True, ipady=3)
        return combo

    def _crear_radios(self):
        fila = tk.Frame(self.contenedor, bg="#FFD700")
        fila.pack(fill="x", anchor="w")
        variables = {}
        for clave, texto in (("cucurucho", "Cucurucho"), ("cono", "Cono"), ("nieve", "Con nieve")):
            variables[clave] = tk.StringVar(value="")
            tk.Radiobutton(
                fila,
                text=texto,
                value=clave,
                variable=variables[clave],
                bg="#FFD700",
                fg="#333333",
                activebackground="#FFD700",
                activeforeground="#333333",
                selectcolor="#FFD700",
                font=("Segoe UI", 10),
                padx=6,
            ).pack(side="left")
        return (
            variables["cucurucho"],
            variables["cono"],
            variables["nieve"],
        )

    def _crear_boton(self, padre, texto, color, comando):
        boton = tk.Button(
            padre,
            text=texto,
            bg=color,
            fg="white",
            activebackground=color,
            activeforeground="white",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            bd=0,
            padx=22,
            pady=8,
            cursor="hand2",
            command=comando,
        )
        boton.pack(side="left", padx=(0, 10) if texto == "Confirmar Pedido" else 0, expand=True)
        return boton

    def _quitar_placeholder(self, evento):
        widget = evento.widget
        placeholder = getattr(widget, "_placeholder", None)
        actual = widget.get("1.0", "end") if widget is self.texto_obs else widget.get()
        if placeholder and actual.strip() == placeholder:
            widget.delete("1.0", "end")
            widget.config(fg="#333333")

    def _restaurar_placeholder(self, evento):
        widget = evento.widget
        placeholder = getattr(widget, "_placeholder", None)
        if not placeholder:
            return
        actual = widget.get("1.0", "end") if widget is self.texto_obs else widget.get()
        if not actual.strip():
            if widget is self.texto_obs:
                widget.insert("1.0", placeholder)
            else:
                widget.insert(0, placeholder)
            widget.config(fg="#999999")

    def cerrar(self):
        if messagebox.askyesno("Confirmar salida", "Seguro que quieres salir?"):
            self.master.destroy()

    def confirmar_pedido(self):
        def valor_de(widget):
            texto = widget.get().strip()
            return "" if texto == widget._placeholder else texto

        nombre = valor_de(self.campo_nombre)
        if not nombre:
            self.resultado.config(text="Por favor escribe tu nombre.")
            return

        sabor = self.combo_sabor.get()
        topping = self.combo_topping.get()

        cantidad = valor_de(self.campo_cantidad) or "1"

        extras = []
        if self.radio_cucurucho.get():
            extras.append("Cucurucho")
        if self.radio_cono.get():
            extras.append("Cono")
        if self.radio_nieve.get():
            extras.append("Con nieve")
        extras_str = ", ".join(extras) if extras else "Ninguno"

        para_llevar = "Si" if self.var_llevar.get() else "No"

        messagebox.showinfo(
            "Pedido Confirmado",
            f"Cliente: {nombre}\n"
            f"Sabor: {sabor}\n"
            f"Topping: {topping}\n"
            f"Cantidad: {cantidad}\n"
            f"Extras: {extras_str}\n"
            f"Para llevar: {para_llevar}",
        )

        self.resultado.config(text=f"Pedido listo para {nombre} - {sabor} x{cantidad}")

    def limpiar(self):
        self.campo_nombre.delete(0, "end")
        self.combo_sabor.current(0)
        self.combo_topping.current(0)
        self.campo_cantidad.delete(0, "end")
        self.radio_cucurucho.set("")
        self.radio_cono.set("")
        self.radio_nieve.set("")
        self.var_llevar.set(0)
        self.texto_obs.delete("1.0", "end")
        self.resultado.config(text="")


if __name__ == "__main__":
    app = VentanaBienvenida()
    app.mainloop()
