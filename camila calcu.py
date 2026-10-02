"""Calculadora Rosa & Morada en Tkinter, con historial de las ultimas 5 operaciones.

    python "camila calcu.py"
"""

import math
import tkinter as tk
from tkinter import font as tkfont

AUTOR = "Camil Fuentes"
MAX_HISTORIAL = 5

# Colores con contraste minimo 4.5:1 (WCAG AA) entre el texto y su fondo.
FONDO = "#c77dff"
PANEL = "#f7e6ff"
PANTALLA = "#7b1fa2"
TINTAPANTALLA = "#ffe6f5"
TINTAERROR = "#ffffff"
FONDOERROR = "#c2185b"
TINTAHIST = "#6a1b9a"
TINTAHIST_VACIO = "#8e24aa"
TINTAAVISO = "#c2185b"
TINTACREDITO = "#380d6e"

ESTILOS = {
    # hover_fg va aparte porque al oscurecer el fondo el texto claro ya no
    # se lee: el morado de los numeros sobre rosa oscuro daba 2.4:1.
    "num":     {"bg": "#ff9ce0", "fg": "#4a148c", "hover": "#d81b60", "hover_fg": "#ffffff"},
    "op":      {"bg": "#9e40ae", "fg": "#fff3fb", "hover": "#7b1fa2", "hover_fg": "#ffffff"},
    "igual":   {"bg": "#6a1b9a", "fg": "#ffffff",  "hover": "#4a148c", "hover_fg": "#ffffff"},
    "limpiar": {"bg": "#cc1857", "fg": "#ffffff",  "hover": "#b01248", "hover_fg": "#ffffff"},
}


class Calculo:
    """La logica de la calculadora, sin dependencias de la ventana."""

    SIMBOLOS = {"+": "+", "-": "-", "*": "\u00d7", "/": "\u00f7"}
    MAX_HISTORIAL = MAX_HISTORIAL

    def __init__(self):
        self.actual = "0"       # el numero que se esta escribiendo
        self.anterior = None    # operando izquierdo
        self.operador = None    # + - * /
        self.reiniciar = False  # el proximo digito empieza un numero nuevo
        self.error = None       # texto corto que va en la pantalla
        self.detalle = None     # explicacion que va debajo de la pantalla
        self.vista = None       # texto a mostrar con el operador pendiente
        self.historial = []     # las ultimas MAX_HISTORIAL operaciones

    @property
    def texto(self):
        if self.error:
            return self.error
        return self.actual if self.vista is None else self.vista

    @property
    def historial_texto(self):
        """Historial para pintar, con la operacion mas reciente arriba."""
        return "\n".join(reversed(self.historial))

    # ------------------------------------------------------------------
    # historial
    # ------------------------------------------------------------------
    def _empujar(self, linea):
        """Agrega una linea dejando solo las ultimas MAX_HISTORIAL."""
        if self.error:
            return
        if self.historial and self.historial[-1] == linea:
            return                      # evita repetir la misma linea seguida
        self.historial.append(linea)
        # OJO: con del h[:-MAX] cuando len(h) <= MAX el slice queda vacio y
        # se borraria todo el historial. Hay que recortar la lista entera.
        if len(self.historial) > self.MAX_HISTORIAL:
            del self.historial[: -self.MAX_HISTORIAL]

    def anotar(self, a, op, b):
        """Operacion binaria: 2 + 3 = 5"""
        self._empujar(
            "{} {} {} = {}".format(
                self.redondear(a), self.SIMBOLOS[op], self.redondear(b), self.actual
            )
        )

    def anotar_simple(self, etiqueta, antes):
        """Operacion unaria: \u221a 16 = 4"""
        self._empujar("{} {} = {}".format(etiqueta, antes, self.actual))

    def borrar_historial(self):
        self.historial = []
        return self

    def _ya_registrado(self, valor):
        """True si el valor ya es el resultado de la ultima linea del historial."""
        if not self.historial:
            return False
        return self.historial[-1].split("= ")[-1] == valor

    # ------------------------------------------------------------------
    # entrada
    # ------------------------------------------------------------------
    def escribir(self, n):
        if len(n) != 1 or n not in "0123456789.":
            return self
        if self.error:
            self.limpiar()
        self.vista = None
        if self.reiniciar:
            # Empieza un numero nuevo. Si el primero es punto hace falta el
            # cero delante, si no se veria ".5" en vez de "0.5".
            self.actual = "0." if n == "." else n
            self.reiniciar = False
        elif self.actual == "0" and n != ".":
            self.actual = n
        elif n == "." and "." in self.actual:
            return self
        else:
            self.actual += n
        return self

    def calc(self, op):
        if self.error:
            return self
        self.vista = None
        if self.operador is not None and not self.reiniciar:
            if not self.calcular():
                return self
        try:
            self.anterior = float(self.actual)
        except ValueError:
            self._fallar("!ERROR!", "Numero no valido")
            return self
        self.operador = op
        self.reiniciar = True
        self.vista = self.redondear(self.anterior) + " " + self.SIMBOLOS[op]
        return self

    def calcular(self):
        """Ejecuta la operacion pendiente. False si hubo error."""
        if self.anterior is None or self.operador is None:
            return True

        b = float(self.actual)
        op = self.operador
        a = self.anterior
        self.anterior = None
        self.operador = None

        if op == "/" and b == 0:
            self._fallar("!ERROR!", "No se puede dividir entre 0")
            return False

        try:
            if op == "+":
                r = a + b
            elif op == "-":
                r = a - b
            elif op == "*":
                r = a * b
            else:
                r = a / b
        except (ValueError, ZeroDivisionError, OverflowError):
            self._fallar("!ERROR!", "Operacion no valida")
            return False

        try:
            self.actual = self.redondear(r)
        except ValueError:
            self._fallar("!ERROR!", "El resultado es muy grande")
            return False
        self.anotar(a, op, b)
        return True

    def resultado(self):
        if self.error:
            return self
        self.vista = None
        pendiente = self.anterior is not None and self.operador is not None
        if not self.calcular():
            return self
        if not pendiente and not self._ya_registrado(self.actual):
            # "=" sin operacion pendiente solo deja el numero en el historial,
            # y solo si no es el resultado que ya aparece arriba.
            self._empujar(self.actual)
        self.reiniciar = True
        return self

    def raiz(self):
        return self.aplicar(
            math.sqrt, "No hay raiz de un numero negativo",
            solo_positivo=True, etiqueta="\u221a",
        )

    def porcentaje(self):
        return self.aplicar(lambda n: n / 100, etiqueta="%")

    def signo(self):
        return self.aplicar(lambda n: -n, etiqueta="\u00b1")

    def aplicar(self, f, mensaje_error=None, solo_positivo=False, etiqueta=None):
        """Aplica f al numero actual, con guarda de errores."""
        if self.error:
            return self
        try:
            n = float(self.actual)
        except ValueError:
            self._fallar("!ERROR!", "Numero no valido")
            return self
        if solo_positivo and n < 0:
            self._fallar("!ERROR!", mensaje_error)
            return self
        try:
            self.actual = self.redondear(f(n))
        except (ValueError, OverflowError):
            self._fallar("!ERROR!", mensaje_error or "Resultado no valido")
            return self
        self.vista = None
        self.reiniciar = True
        if etiqueta:
            self.anotar_simple(etiqueta, self.redondear(n))
        return self

    def borrar(self):
        if self.error:
            return self.limpiar()
        if self.vista is not None:
            self.vista = None
            return self
        self.actual = self.actual[:-1] if len(self.actual) > 1 else "0"
        if self.actual in ("", "-", "."):
            self.actual = "0"
        return self

    def limpiar(self):
        """Borra la cuenta en curso. El historial se conserva."""
        historial = self.historial
        self.__init__()
        self.historial = historial
        return self

    def _fallar(self, corto, detalle):
        self.error = corto
        self.detalle = detalle
        self.anterior = None
        self.operador = None
        self.vista = None

    @staticmethod
    def redondear(n):
        if not math.isfinite(n):
            raise ValueError("resultado infinito")
        r = round(n, 10)
        return str(int(r)) if r == int(r) else str(r)


class Calculadora:
    """La ventana. Los botones solo delegan en Calculo."""

    def __init__(self, raiz=None):
        self.logica = Calculo()
        self.raiz = raiz if raiz is not None else tk.Tk()
        self.raiz.title("Calculadora Rosa & Morada")
        self.raiz.configure(bg=FONDO)
        self.raiz.resizable(False, False)

        self.fuente_pantalla = tkfont.Font(family="Consolas", size=26, weight="bold")
        self.botones = {}

        self._construir()
        self.raiz.update_idletasks()
        # Ancho de la pantalla con la fuente grande, medido una sola vez.
        # Sirve para dos cosas: saber cuanto texto cabe sin recortarse y
        # fijar el ancho de la columna, para que al achicar la fuente
        # la ventana no encoja y luego crezca.
        self.ancho_caja = self.pantalla.winfo_reqwidth()
        self.marco.columnconfigure(0, minsize=self.ancho_caja)
        self.pintar()

    # ------------------------------------------------------------------
    # construccion
    # ------------------------------------------------------------------
    def _construir(self):
        marco = tk.Frame(self.raiz, bg=PANEL)
        marco.pack(padx=18, pady=18)
        marco.columnconfigure(0, weight=1)
        self.marco = marco

        self.pantalla = tk.Label(
            marco,
            text="0",
            font=self.fuente_pantalla,
            bg=PANTALLA,
            fg=TINTAPANTALLA,
            anchor="e",
            justify="right",
            padx=14,
            pady=14,
            width=16,
        )
        self.pantalla.grid(row=0, column=0, sticky="ew", pady=(14, 2))

        # Explicacion del error, para no recortarlo dentro de la pantalla.
        self.aviso = tk.Label(
            marco,
            text="",
            font=("Segoe UI", 9),
            bg=PANEL,
            fg=TINTAAVISO,
            anchor="e",
            justify="right",
            wraplength=300,
        )
        self.aviso.grid(row=1, column=0, sticky="ew")

        # Historial: las ultimas MAX_HISTORIAL operaciones, la mas reciente arriba.
        # Es un Text para que las lineas largas no ensanchen la ventana.
        # OJO: tk.Text no tiene -justify, la alineacion va por etiqueta.
        self.historial = tk.Text(
            marco,
            height=MAX_HISTORIAL,
            width=16,
            font=("Consolas", 10),
            bg=PANEL,
            fg=TINTAHIST,
            bd=0,
            highlightthickness=0,
            relief="flat",
            wrap="word",
            cursor="arrow",
            padx=2,
            pady=2,
        )
        self.historial.tag_configure("der", justify="right")
        self.historial.grid(row=2, column=0, sticky="ew", pady=(6, 10))
        self.historial.config(state="disabled")
        self.historial.bind("<Double-Button-1>", self._doble_clic_historial)

        teclado = tk.Frame(marco, bg=PANEL)
        teclado.grid(row=3, column=0, sticky="ew")
        self._crear_botones(teclado)

        self.credito = tk.Label(
            marco,
            text="Creado por %s" % AUTOR,
            font=("Segoe UI", 8),
            bg=PANEL,
            fg=TINTACREDITO,
            anchor="e",
        )
        self.credito.grid(row=4, column=0, sticky="ew", padx=14, pady=(8, 0))

    def _crear_botones(self, teclado):
        C, L = self.logica, self.logica.limpiar
        filas = [
            [("AC", self.nueva_cuenta, "limpiar"),
             ("\u221a", C.raiz, "op"),
             ("%", C.porcentaje, "op")],
            [("7", self._digito("7"), "num"), ("8", self._digito("8"), "num"),
             ("9", self._digito("9"), "num")],
            [("4", self._digito("4"), "num"), ("5", self._digito("5"), "num"),
             ("6", self._digito("6"), "num")],
            [("1", self._digito("1"), "num"), ("2", self._digito("2"), "num"),
             ("3", self._digito("3"), "num")],
            [("0", self._digito("0"), "num"), (".", self._punto, "num"),
             ("\u00b1", C.signo, "op")],
            [("\u00f7", self._operacion("/"), "op"), ("\u00d7", self._operacion("*"), "op"),
             ("+", self._operacion("+"), "op")],
            [("\u2212", self._operacion("-"), "op"), ("C", self.limpiar_cuenta, "limpiar"),
             ("=", C.resultado, "igual")],
        ]

        for fila in filas:
            f = tk.Frame(teclado, bg=PANEL)
            f.pack()
            for texto, accion, estilo in fila:
                b = self._nuevo_boton(f, texto, accion, estilo)
                self.botones[texto] = b

    def _nuevo_boton(self, padre, texto, accion, estilo):
        e = ESTILOS[estilo]
        b = tk.Button(
            padre,
            text=texto,
            command=lambda a=accion: self.pulsar(a),
            width=6,
            height=2,
            font=("Segoe UI", 14, "bold"),
            bg=e["bg"],
            fg=e["fg"],
            activebackground=e["hover"],
            activeforeground=e["hover_fg"],
            relief="flat",
            bd=0,
            cursor="hand2",
            highlightthickness=0,
            takefocus=0,
        )
        b.pack(side="left", padx=4, pady=4)
        return b

    def _digito(self, n):
        return lambda: self.logica.escribir(n)

    def _punto(self):
        return self.logica.escribir(".")

    def _operacion(self, op):
        return lambda: self.logica.calc(op)

    # ------------------------------------------------------------------
    # acciones
    # ------------------------------------------------------------------
    def pulsar(self, accion):
        """Ejecuta la accion y DESPUES repinta.

        Antes se repintaba en <Button-1>, que Tk dispara en el press, antes
        del command: la pantalla mostraba el dato viejo. Ahora el repintado va
        aqui, cuando la accion ya se aplico.
        """
        accion()
        self.pintar()

    def limpiar_cuenta(self):
        self.logica.limpiar()

    def nueva_cuenta(self):
        self.logica.limpiar()
        self.logica.borrar_historial()

    def borrar_historial(self):
        self.logica.borrar_historial()
        self.pintar()

    def _doble_clic_historial(self, evento=None):
        self.borrar_historial()

    # ------------------------------------------------------------------
    # pintado
    # ------------------------------------------------------------------
    def pintar(self):
        texto = self.logica.texto
        error = bool(self.logica.error)

        self._ajustar_fuente(texto)
        self.pantalla.config(
            text=texto,
            bg=FONDOERROR if error else PANTALLA,
            fg=TINTAERROR if error else TINTAPANTALLA,
        )
        self.aviso.config(text=self.logica.detalle or "")

        self.historial.config(state="normal")
        self.historial.delete("1.0", "end")
        if self.logica.historial:
            self.historial.insert("1.0", self.logica.historial_texto, "der")
            self.historial.config(fg=TINTAHIST)
        else:
            self.historial.insert("1.0", "sin operaciones aun", "der")
            self.historial.config(fg=TINTAHIST_VACIO)
        self.historial.config(state="disabled")

    def _ajustar_fuente(self, texto):
        """Baja el tamano hasta que el numero quepa sin recortarse."""
        disponible = max(40, self.ancho_caja - 8)
        for size in (26, 22, 19, 16, 13, 11):
            self.fuente_pantalla.configure(size=size)
            if self.fuente_pantalla.measure(texto) <= disponible:
                break
        self.pantalla.config(font=self.fuente_pantalla)

    # ------------------------------------------------------------------
    # teclado
    # ------------------------------------------------------------------
    def pulsar_tecla(self, evento):
        k = evento.keysym
        C = self.logica
        # El teclado numerico llega como "KP_5", no como "5".
        if k.startswith("KP_") and len(k) > 3 and k[3:].isdigit():
            C.escribir(k[3])
        elif k and len(k) == 1 and k.isdigit():
            C.escribir(k)
        elif k in ("period", "KP_Decimal", "KP_Divisor"):
            C.escribir(".")
        elif k in ("plus", "K_Add", "KP_Add"):
            C.calc("+")
        elif k in ("minus", "K_Subtract", "KP_Subtract"):
            C.calc("-")
        elif k in ("asterisk", "K_Multiply", "KP_Multiply"):
            C.calc("*")
        elif k in ("slash", "K_Divide", "KP_Divide"):
            C.calc("/")
        elif k in ("Return", "KP_Enter", "equal"):
            C.resultado()
        elif k == "BackSpace":
            C.borrar()
        elif k == "Escape":
            C.limpiar()
        else:
            return
        self.pintar()

    def iniciar(self):
        self.raiz.bind("<Key>", self.pulsar_tecla)
        self.raiz.mainloop()


def main():
    Calculadora().iniciar()


if __name__ == "__main__":
    main()