"""
Sistema de pedidos de "La Heladería" hecho con Toga (Beeware).

Pantalla de bienvenida -> formulario de pedido -> tabla con los pedidos ya
registrados y su total.

Ejecutar con:  python heladeria_toga.py
"""

from dataclasses import dataclass

import toga
from toga.style import Pack

# --------------------------------------------------------------------------
# Paleta de colores y datos de la heladería
# --------------------------------------------------------------------------
ROSA = "#FFC1D6"
ROSA_OSCURO = "#FF9EC0"
DORADO = "#FFD700"
MORADO = "#800080"
BLANCO = "#FFFFFF"
TEXTO = "#333333"
TEXTO_TENUE = "#8A6A8A"

SABORES = ["Vainilla", "Chocolate", "Fresa", "Menta", "Dulce de leche", "Frutilla"]
TOPPINGS = [
    "Ninguno",
    "Salsa de chocolate",
    "Salsa de fresa",
    "Chispas de colores",
    "Oreo",
    "Cerezas",
]
ENVASES = ["Cucurucho", "Cono", "Copa"]

PRECIO_SABOR = {
    "Vainilla": 2500,
    "Chocolate": 2800,
    "Fresa": 2700,
    "Menta": 2600,
    "Dulce de leche": 3000,
    "Frutilla": 2900,
}
PRECIO_TOPPING = {
    "Ninguno": 0,
    "Salsa de chocolate": 600,
    "Salsa de fresa": 600,
    "Chispas de colores": 500,
    "Oreo": 700,
    "Cerezas": 800,
}
PRECIO_ENVASE = {"Cucurucho": 2500, "Cono": 3000, "Copa": 4000}


def pesos(valor):
    """Formatea un número con el estilo de pesos: $12.500"""
    return "$" + f"{valor:,.0f}".replace(",", ".")


@dataclass
class Pedido:
    cliente: str
    sabor: str
    topping: str
    cantidad: int
    envase: str
    para_llevar: bool
    observaciones: str

    @property
    def total(self):
        return (PRECIO_SABOR[self.sabor] + PRECIO_TOPPING[self.topping]) * self.cantidad + PRECIO_ENVASE[self.envase]

    def resumen(self):
        return [
            ("Cliente", self.cliente),
            ("Sabor", self.sabor),
            ("Topping", self.topping),
            ("Cantidad", str(self.cantidad)),
            ("Envase", self.envase),
            ("Para llevar", "Sí" if self.para_llevar else "No"),
            ("Observaciones", self.observaciones or "Ninguna"),
            ("TOTAL", pesos(self.total)),
        ]

    def fila(self):
        return {
            "cliente": self.cliente,
            "sabor": self.sabor,
            "topping": self.topping,
            "envase": self.envase,
            "cantidad": str(self.cantidad),
            "total": pesos(self.total),
        }


class Heladeria(toga.App):
    def __init__(self):
        super().__init__(
            formal_name="La Heladería",
            app_id="com.camila.heladeria",
            author="Camila Marcela",
            version="1.0",
            description="Sistema de pedidos de La Heladería",
            startup=self.arrancar,
        )
        self.pedidos = []
        self.sincronizando_envase = False
        self.campos = {}

    # ------------------------------------------------------------------
    # Pantalla de bienvenida
    # ------------------------------------------------------------------
    def arrancar(self):
        ventana = self.main_window
        ventana.title = "La Heladería"
        ventana.size = (940, 660)
        ventana.content = self.armar_bienvenida()
        ventana.show()

    def armar_bienvenida(self):
        return toga.Box(
            style=Pack(
                direction="column",
                align_items="center",
                justify_content="center",
                background_color=ROSA,
                padding=30,
                gap=6,
            ),
            children=[
                toga.Label(
                    "La Heladería",
                    style=Pack(font_size=36, font_weight="bold", color=MORADO),
                ),
                toga.Label(
                    "Los mejores sabores de la ciudad",
                    style=Pack(font_size=12, color=MORADO, margin_bottom=24),
                ),
                toga.Box(
                    style=Pack(
                        direction="column",
                        background_color=BLANCO,
                        padding=(20, 40),
                        margin_bottom=24,
                        gap=4,
                    ),
                    children=[
                        toga.Label(
                            "Sabores",
                            style=Pack(font_weight="bold", color=ROSA_OSCURO),
                        ),
                        toga.Label(
                            ", ".join(SABORES),
                            style=Pack(font_size=11, color=TEXTO),
                        ),
                        toga.Label(
                            "Envases: cucurucho, cono o copa",
                            style=Pack(font_size=11, color=TEXTO),
                        ),
                    ],
                ),
                toga.Button(
                    "Entrar",
                    on_press=self.abrir_sistema,
                    style=Pack(
                        background_color=DORADO,
                        color=MORADO,
                        font_weight="bold",
                        font_size=14,
                        padding=(10, 40),
                    ),
                ),
                toga.Label(
                    "Creado por Camila Marcela",
                    style=Pack(font_size=10, font_style="italic", color=MORADO, margin_top=28),
                ),
            ],
        )

    def abrir_sistema(self, widget, **kwargs):
        self.pedidos = []
        ventana = self.main_window
        ventana.title = "La Heladería - Sistema de Pedidos"
        ventana.size = (960, 660)
        ventana.content = self.armar_sistema()
        ventana.show()

    def volver_al_inicio(self, widget, **kwargs):
        ventana = self.main_window
        ventana.title = "La Heladería"
        ventana.content = self.armar_bienvenida()
        ventana.show()

    # ------------------------------------------------------------------
    # Pantalla del sistema de pedidos
    # ------------------------------------------------------------------
    def armar_sistema(self):
        # ---- datos del cliente -------------------------------------------
        campo_nombre = toga.TextInput(
            placeholder="Escribe tu nombre...",
            style=Pack(flex=1),
        )
        campo_sabor = toga.Selection(
            items=SABORES,
            value=SABORES[0],
            on_change=self.actualizar_total,
            style=Pack(flex=1),
        )
        campo_topping = toga.Selection(
            items=TOPPINGS,
            value=TOPPINGS[0],
            on_change=self.actualizar_total,
            style=Pack(flex=1),
        )
        campo_cantidad = toga.NumberInput(
            min=1,
            max=20,
            value=1,
            on_change=self.actualizar_total,
            style=Pack(width=80),
        )
        campo_obs = toga.MultilineTextInput(
            placeholder="Escribe alergias, preferencias o instrucciones especiales...",
            style=Pack(flex=1, height=80),
        )
        campo_llevar = toga.Switch(
            "Pedido para llevar",
            value=False,
            on_change=self.actualizar_total,
        )

        self.switches_envase = [
            toga.Switch(nombre, value=(nombre == ENVASES[0]), on_change=self.elegir_envase)
            for nombre in ENVASES
        ]

        self.etiqueta_total = toga.Label(
            "TOTAL: $0",
            style=Pack(font_size=16, font_weight="bold", color=MORADO),
        )
        self.etiqueta_resultado = toga.Label(
            "Completa el formulario y presiona Confirmar Pedido.",
            style=Pack(font_size=11, color=TEXTO, margin_top=8),
        )

        self.tabla = toga.Table(
            headings=["Cliente", "Sabor", "Topping", "Envase", "Cant.", "Total"],
            accessors=["cliente", "sabor", "topping", "envase", "cantidad", "total"],
            data=[],
            style=Pack(flex=1),
        )

        self.campos = {
            "nombre": campo_nombre,
            "sabor": campo_sabor,
            "topping": campo_topping,
            "cantidad": campo_cantidad,
            "observaciones": campo_obs,
            "llevar": campo_llevar,
        }

        formulario = toga.Box(
            style=Pack(
                direction="column",
                background_color=DORADO,
                padding=16,
                width=380,
                gap=10,
            ),
            children=[
                toga.Label(
                    "Datos del pedido",
                    style=Pack(font_size=16, font_weight="bold", color=MORADO, margin_bottom=4),
                ),
                self.fila_etiqueta("Nombre del cliente:", campo_nombre),
                self.fila_etiqueta("Sabor del helado:", campo_sabor),
                self.fila_etiqueta("Topping extra:", campo_topping),
                self.fila_etiqueta("Cantidad:", campo_cantidad),
                toga.Label(
                    "Opciones extra:",
                    style=Pack(font_weight="bold", color=TEXTO),
                ),
                toga.Row(
                    style=Pack(gap=12),
                    children=list(self.switches_envase),
                ),
                campo_llevar,
                toga.Label(
                    "Observaciones:",
                    style=Pack(font_weight="bold", color=TEXTO, margin_top=6),
                ),
                campo_obs,
                toga.Divider(style=Pack(margin=6)),
                self.etiqueta_total,
                self.etiqueta_resultado,
                toga.Row(
                    style=Pack(gap=8, margin_top=12),
                    children=[
                        toga.Button(
                            "Confirmar Pedido",
                            on_press=self.confirmar_pedido,
                            style=Pack(
                                flex=1,
                                background_color=ROSA_OSCURO,
                                color=BLANCO,
                                font_weight="bold",
                                padding=8,
                            ),
                        ),
                        toga.Button(
                            "Limpiar",
                            on_press=self.limpiar,
                            style=Pack(background_color=MORADO, color=BLANCO, padding=8),
                        ),
                    ],
                ),
                toga.Row(
                    style=Pack(gap=8, margin_top=8),
                    children=[
                        toga.Button(
                            "Borrar seleccionado",
                            on_press=self.borrar_seleccion,
                            style=Pack(
                                flex=1,
                                background_color=BLANCO,
                                color=MORADO,
                                padding=8,
                            ),
                        ),
                        toga.Button(
                            "Volver",
                            on_press=self.volver_al_inicio,
                            style=Pack(background_color=BLANCO, color=MORADO, padding=8),
                        ),
                    ],
                ),
            ],
        )

        lista_pedidos = toga.Box(
            style=Pack(
                direction="column",
                flex=1,
                background_color=BLANCO,
                padding=16,
                gap=8,
            ),
            children=[
                toga.Row(
                    style=Pack(align_items="center", gap=10),
                    children=[
                        toga.Label(
                            "Pedidos registrados",
                            style=Pack(font_size=16, font_weight="bold", color=MORADO),
                        ),
                        toga.Label(
                            "0 pedidos",
                            id="contador",
                            style=Pack(font_size=11, color=TEXTO_TENUE),
                        ),
                    ],
                ),
                toga.Divider(),
                self.tabla,
                toga.Label(
                    "Creado por Camila Marcela",
                    style=Pack(font_size=10, font_style="italic", color=TEXTO_TENUE),
                ),
            ],
        )

        self.etiqueta_contador = lista_pedidos.children[0].children[1]

        return toga.Box(
            style=Pack(direction="column", background_color=ROSA_OSCURO, padding=10, gap=10),
            children=[
                toga.Row(
                    style=Pack(align_items="center"),
                    children=[
                        toga.Label(
                            "La Heladería",
                            style=Pack(font_size=22, font_weight="bold", color=MORADO),
                        ),
                        toga.Label(
                            "Sistema de pedidos",
                            style=Pack(font_size=12, color=TEXTO, margin_left=12),
                        ),
                    ],
                ),
                toga.Row(
                    style=Pack(flex=1, gap=10),
                    children=[formulario, lista_pedidos],
                ),
            ],
        )

    def fila_etiqueta(self, texto, campo):
        """Arma una fila con la etiqueta a la izquierda y el campo a la derecha."""
        return toga.Row(
            style=Pack(align_items="center", gap=8),
            children=[
                toga.Label(
                    texto,
                    style=Pack(width=150, font_size=11, font_weight="bold", color=TEXTO),
                ),
                campo,
            ],
        )

    # ------------------------------------------------------------------
    # Lógica del formulario
    # ------------------------------------------------------------------
    def elegir_envase(self, widget, **kwargs):
        """Los Switch del envase se comportan como botones de opción."""
        if self.sincronizando_envase:
            return
        self.sincronizando_envase = True
        try:
            for switch in self.switches_envase:
                switch.value = switch.text == widget.text
        finally:
            self.sincronizando_envase = False
        self.actualizar_total()

    def envase_elegido(self):
        for switch in self.switches_envase:
            if switch.value:
                return switch.text
        return ENVASES[0]

    def cantidad_elegida(self):
        valor = self.campos["cantidad"].value
        if valor is None:
            return 1
        return max(1, int(valor))

    def calcular_total(self):
        sabor = self.campos["sabor"].value
        topping = self.campos["topping"].value
        cantidad = self.cantidad_elegida()
        envase = self.envase_elegido()
        return (PRECIO_SABOR[sabor] + PRECIO_TOPPING[topping]) * cantidad + PRECIO_ENVASE[envase]

    def actualizar_total(self, widget=None, **kwargs):
        self.etiqueta_total.text = f"TOTAL: {pesos(self.calcular_total())}"

    # ------------------------------------------------------------------
    # Botones
    # ------------------------------------------------------------------
    async def confirmar_pedido(self, widget, **kwargs):
        nombre = self.campos["nombre"].value.strip()
        if not nombre:
            self.etiqueta_resultado.text = "Por favor escribe tu nombre."
            await self.main_window.dialog(
                toga.InfoDialog("Faltan datos", "Por favor escribe tu nombre para confirmar el pedido.")
            )
            return

        cantidad = self.cantidad_elegida()
        pedido = Pedido(
            cliente=nombre,
            sabor=self.campos["sabor"].value,
            topping=self.campos["topping"].value,
            cantidad=cantidad,
            envase=self.envase_elegido(),
            para_llevar=self.campos["llevar"].value,
            observaciones=self.campos["observaciones"].value.strip(),
        )

        self.pedidos.append(pedido.fila())
        self.refrescar_tabla()

        lineas = "\n".join(f"{etiqueta}: {valor}" for etiqueta, valor in pedido.resumen())
        self.etiqueta_resultado.text = (
            f"Pedido listo para {pedido.cliente} - {pedido.sabor} x{pedido.cantidad}"
        )
        await self.main_window.dialog(toga.InfoDialog("Pedido confirmado", lineas))
        self.limpiar(widget)

    def limpiar(self, widget=None, **kwargs):
        self.campos["nombre"].value = ""
        self.campos["sabor"].value = SABORES[0]
        self.campos["topping"].value = TOPPINGS[0]
        self.campos["cantidad"].value = 1
        self.campos["observaciones"].value = ""
        self.campos["llevar"].value = False
        for switch in self.switches_envase:
            switch.value = switch.text == ENVASES[0]
        self.etiqueta_resultado.text = "Formulario limpio. Puedes tomar el siguiente pedido."
        self.actualizar_total()

    def borrar_seleccion(self, widget, **kwargs):
        if not self.tabla.selection:
            self.etiqueta_resultado.text = "Primero selecciona un pedido de la tabla."
            return
        self.pedidos.pop(self.tabla.selection[0])
        self.refrescar_tabla()
        self.etiqueta_resultado.text = "Pedido eliminado de la lista."

    def refrescar_tabla(self):
        self.tabla.data = list(self.pedidos)
        self.etiqueta_contador.text = f"{len(self.pedidos)} pedido{'s' if len(self.pedidos) != 1 else ''}"

    async def salir(self, widget, **kwargs):
        confirmado = await self.main_window.dialog(
            toga.QuestionDialog("Confirmar salida", "Seguro que quieres salir de La Heladería?")
        )
        if confirmado:
            self.exit()


def main():
    Heladeria().main_loop()


if __name__ == "__main__":
    main()
