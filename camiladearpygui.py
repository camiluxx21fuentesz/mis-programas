"""Calculadora Rosa & Morada con DearPyGui.

Todo corre en este mismo archivo.

    pip install dearpygui
    python camila.py
"""

import math

import dearpygui.dearpygui as dpg


class Calculo:
    """La logica de la calculadora, sin dependencias de la ventana."""

    SIMBOLOS = {"+": "+", "-": "-", "*": "\u00d7", "/": "\u00f7"}
    MAX_HISTORIAL = 5

    def __init__(self):
        self.actual = "0"      # el numero que se esta escribiendo
        self.anterior = None   # operando izquierdo
        self.operador = None   # + - * /
        self.reiniciar = False # el proximo digito empieza un numero nuevo
        self.error = None
        self.vista = None      # texto a mostrar con el operador pendiente
        self.historial = []    # ultimas operaciones, la mas reciente al final

    @property
    def texto(self):
        if self.error:
            return self.error
        return self.actual if self.vista is None else self.vista

    @property
    def historial_texto(self):
        """Historial para pintar, con la operacion mas reciente arriba."""
        return "\n".join(reversed(self.historial))

    def escribir(self, n):
        if len(n) != 1 or n not in "0123456789.":
            return self
        if self.error:
            self.limpiar()
        self.vista = None
        if self.reiniciar or (self.actual == "0" and n != "."):
            self.actual = n
            self.reiniciar = False
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
        self.anterior = float(self.actual)
        self.operador = op
        self.reiniciar = True
        self.vista = self.redondear(self.anterior) + " " + self.SIMBOLOS[op]
        return self

    def calcular(self):
        """Ejecuta la operacion pendiente. Devuelve False si hubo error."""
        if self.anterior is None or self.operador is None:
            return True

        b = float(self.actual)
        op = self.operador
        a = self.anterior
        self.anterior = None
        self.operador = None

        if op == "/" and b == 0:
            self.error = "!ERROR! No se puede dividir entre 0"
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
            self.actual = self.redondear(r)
        except (ValueError, ZeroDivisionError, OverflowError):
            self.error = "!ERROR! Operacion no valida"
            return False
        self.anotar(a, op, b)
        return True

    def _empujar(self, linea):
        """Agrega una linea al historial dejando solo las ultimas 5."""
        self.historial.append(linea)
        # OJO: con del h[:-MAX] cuando len(h) <= MAX el slice es vacio
        # y se borraria todo el historial. Hay que recortar la lista entera.
        if len(self.historial) > self.MAX_HISTORIAL:
            del self.historial[: -self.MAX_HISTORIAL]

    def anotar(self, a, op, b):
        """Guarda el resultado de una operacion binaria: 2 + 3 = 5."""
        self._empujar(
            "{} {} {} = {}".format(
                self.redondear(a), self.SIMBOLOS[op], self.redondear(b), self.actual
            )
        )

    def anotar_simple(self, etiqueta, antes):
        """Guarda el resultado de una operacion unaria: raiz 16 = 4."""
        self._empujar("{} {} = {}".format(etiqueta, antes, self.actual))

    def resultado(self):
        if self.error:
            return self
        self.vista = None
        self.calcular()
        self.reiniciar = True
        return self

    def raiz(self):
        return self.aplicar(
            math.sqrt, "!ERROR! Raiz de numero negativo",
            solo_positivo=True, etiqueta="raiz",
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
            self.error = "!ERROR! Numero no valido"
            return self
        if solo_positivo and n < 0:
            self.error = mensaje_error
            return self
        try:
            self.actual = self.redondear(f(n))
        except (ValueError, OverflowError):
            self.error = mensaje_error or "!ERROR! Resultado no valido"
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

    def borrar_historial(self):
        self.historial = []
        return self

    @staticmethod
    def redondear(n):
        if not math.isfinite(n):
            raise ValueError("resultado infinito")
        r = round(n, 10)
        return str(int(r)) if r == int(r) else str(r)


ANCHO, ALTO = 360, 640

# Geometria del teclado. DearPyGui no reparte bien los temas dentro de un group,
# asi que cada boton se coloca con pos absoluto.
COLUMNAS = [10, 118, 226]
ANCHO_BOTON, ALTO_BOTON = 104, 46
TECLADO_Y, PASO = 196, 54

# Colores en RGBA, cada canal 0-255 (DearPyGui no usa hex).
FONDO = (199, 125, 255, 255)
PANEL = (247, 230, 255, 255)
TITULO = (142, 36, 170, 255)
PANTALLA = (123, 31, 162, 255)
PANTALLA_ERROR = (194, 24, 91, 255)
TINTA_PANTALLA = (255, 230, 245, 255)
TINTA_ERROR = (255, 255, 255, 255)
# Morado oscuro: sobre el panel claro (247,230,255) da ~11:1 de contraste.
# Con un rosa claro el texto quedaba practicamente invisible.
TINTA_HISTORIAL = (106, 27, 154, 255)

# Los colores de boton estan oscurecidos lo justo para que el texto blanco
# alcance 5:1 de contraste (AA pide 4.5:1).
ESTILOS = {
    "num":     ((255, 156, 224, 255), (216, 27, 96, 255),  (74, 20, 140, 255)),
    "op":      ((158, 64, 174, 255),  (123, 31, 162, 255),  (255, 243, 251, 255)),
    "igual":   ((106, 27, 154, 255),  (74, 20, 140, 255),  (255, 255, 255, 255)),
    "limpiar": ((204, 24, 87, 255),   (176, 18, 72, 255),  (255, 255, 255, 255)),
}


def tema_base():
    """Tema global: fondo de la ventana."""
    t = dpg.add_theme()
    c = dpg.add_theme_component(parent=t, item_type=0)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_WindowBg, value=FONDO)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_Text, value=TITULO)
    return t


def tema_lineedit(color_fondo, tinta):
    """Tema para los LineEdit de la pantalla y el historial."""
    t = dpg.add_theme()
    c = dpg.add_theme_component(parent=t, item_type=0)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_FrameBg, value=color_fondo)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_FrameBgHovered, value=color_fondo)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_FrameBgActive, value=color_fondo)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_Text, value=tinta)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_TextSelectedBg, value=tinta)
    dpg.add_theme_style(parent=c, target=dpg.mvStyleVar_FrameRounding, x=12)
    dpg.add_theme_style(parent=c, target=dpg.mvStyleVar_FrameBorderSize, x=0)
    dpg.add_theme_style(parent=c, target=dpg.mvStyleVar_FramePadding, x=8, y=6)
    return t


def tema_boton(estilo):
    normal, hover, tinta = ESTILOS[estilo]
    t = dpg.add_theme()
    c = dpg.add_theme_component(parent=t, item_type=0)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_Button, value=normal)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_ButtonHovered, value=hover)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_ButtonActive, value=hover)
    dpg.add_theme_color(parent=c, target=dpg.mvThemeCol_Text, value=tinta)
    dpg.add_theme_style(parent=c, target=dpg.mvStyleVar_FrameRounding, x=12)
    return t


TEMAS = {}


def crear_temas():
    """Los temas deben crearse FUERA de cualquier contenedor.

    Si se crean dentro de un group, DearPyGui los emparenta a ese group y el
    tema se aplica a todos sus hijos en vez de solo al boton.
    """
    TEMAS["base"] = tema_base()
    TEMAS["pantalla"] = tema_lineedit(PANTALLA, TINTA_PANTALLA)
    TEMAS["pantalla_error"] = tema_lineedit(PANTALLA_ERROR, TINTA_ERROR)
    TEMAS["historial"] = tema_lineedit(PANEL, TINTA_HISTORIAL)
    for nombre in ESTILOS:
        TEMAS[nombre] = tema_boton(nombre)


def pintar(logica):
    """Actualiza los textos de la pantalla y el historial."""
    if logica.error:
        dpg.set_value("linea", "  " + logica.texto)
        dpg.bind_item_theme("linea", TEMAS["pantalla_error"])
    else:
        dpg.set_value("linea", logica.texto.rjust(16))
        dpg.bind_item_theme("linea", TEMAS["pantalla"])
    dpg.set_value("historial", logica.historial_texto)


def construir(logica):
    """Crea la interfaz completa."""
    dpg.create_context()
    crear_temas()
    dpg.bind_theme(TEMAS["base"])

    with dpg.window(
        tag="raiz",
        no_title_bar=True,
        no_move=True,
        no_resize=True,
        no_scrollbar=True,
        width=ANCHO,
        height=ALTO,
    ):
        dpg.add_text("  Calculadora Rosa & Morada")

        # Pantalla: LineEdit de una linea, solo lectura (se escribe con el
        # teclado o los botones, no a mano para no duplicar la entrada).
        dpg.add_input_text(
            tag="linea",
            default_value="0",
            width=ANCHO - 32,
            height=40,
            readonly=True,
            always_overwrite=True,
            no_undo_redo=True,
        )
        dpg.bind_item_theme("linea", TEMAS["pantalla"])

        # Historial: LineEdit multilinea con las ultimas 5 operaciones,
        # la mas reciente arriba.
        dpg.add_input_text(
            tag="historial",
            default_value="",
            width=ANCHO - 32,
            height=Calculo.MAX_HISTORIAL * 17 + 14,
            multiline=True,
            readonly=True,
            always_overwrite=True,
            no_undo_redo=True,
            no_horizontal_scroll=True,
        )
        dpg.bind_item_theme("historial", TEMAS["historial"])

        C = logica

        def boton(texto, accion, estilo, pos):
            b = dpg.add_button(
                label=texto,
                callback=lambda s, a, u: (accion(), pintar(C)),
                pos=pos,
                width=ANCHO_BOTON,
                height=ALTO_BOTON,
            )
            dpg.bind_item_theme(b, TEMAS[estilo])
            return b

        def dig(n):
            return lambda: C.escribir(n)

        def op(sim):
            return lambda: C.calc(sim)

        filas = [
            [("AC", lambda: (C.limpiar(), C.borrar_historial()), "limpiar"),
             ("\u221a", C.raiz, "op"), ("%", C.porcentaje, "op")],
            [("7", dig("7"), "num"), ("8", dig("8"), "num"), ("9", dig("9"), "num")],
            [("4", dig("4"), "num"), ("5", dig("5"), "num"), ("6", dig("6"), "num")],
            [("1", dig("1"), "num"), ("2", dig("2"), "num"), ("3", dig("3"), "num")],
            [("0", dig("0"), "num"), (".", dig("."), "num"), ("\u00b1", C.signo, "op")],
            [("\u00f7", op("/"), "op"), ("\u00d7", op("*"), "op"), ("+", op("+"), "op")],
            [("\u2212", op("-"), "op"), ("C", C.limpiar, "limpiar"),
             ("=", C.resultado, "igual")],
        ]

        y = TECLADO_Y
        for fila in filas:
            for i, (texto, accion, estilo) in enumerate(fila):
                boton(texto, accion, estilo, pos=[COLUMNAS[i], y])
            y += PASO

    dpg.set_primary_window("raiz", True)

    teclas = {
        dpg.mvKey_0: lambda: C.escribir("0"), dpg.mvKey_1: lambda: C.escribir("1"),
        dpg.mvKey_2: lambda: C.escribir("2"), dpg.mvKey_3: lambda: C.escribir("3"),
        dpg.mvKey_4: lambda: C.escribir("4"), dpg.mvKey_5: lambda: C.escribir("5"),
        dpg.mvKey_6: lambda: C.escribir("6"), dpg.mvKey_7: lambda: C.escribir("7"),
        dpg.mvKey_8: lambda: C.escribir("8"), dpg.mvKey_9: lambda: C.escribir("9"),
        dpg.mvKey_NumPad0: lambda: C.escribir("0"),
        dpg.mvKey_NumPad1: lambda: C.escribir("1"),
        dpg.mvKey_NumPad2: lambda: C.escribir("2"),
        dpg.mvKey_NumPad3: lambda: C.escribir("3"),
        dpg.mvKey_NumPad4: lambda: C.escribir("4"),
        dpg.mvKey_NumPad5: lambda: C.escribir("5"),
        dpg.mvKey_NumPad6: lambda: C.escribir("6"),
        dpg.mvKey_NumPad7: lambda: C.escribir("7"),
        dpg.mvKey_NumPad8: lambda: C.escribir("8"),
        dpg.mvKey_NumPad9: lambda: C.escribir("9"),
        dpg.mvKey_Decimal: lambda: C.escribir("."),
        dpg.mvKey_Plus: lambda: C.calc("+"), dpg.mvKey_Minus: lambda: C.calc("-"),
        dpg.mvKey_Multiply: lambda: C.calc("*"), dpg.mvKey_Divide: lambda: C.calc("/"),
        dpg.mvKey_Return: C.resultado, dpg.mvKey_NumPadEnter: C.resultado,
        dpg.mvKey_Back: C.borrar, dpg.mvKey_Escape: C.limpiar,
    }
    with dpg.handler_registry():
        for k, accion in teclas.items():
            dpg.add_key_press_handler(
                key=k,
                callback=lambda s, a, u, f=accion: (f(), pintar(C)),
            )

    dpg.create_viewport(
        title="Calculadora Rosa & Morada", width=ANCHO, height=ALTO
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()
    pintar(C)
    dpg.start_dearpygui()


if __name__ == "__main__":
    construir(Calculo())