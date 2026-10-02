import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox,
                             QFormLayout, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QMessageBox, QPushButton,
                             QRadioButton, QTextEdit, QVBoxLayout, QWidget)


ESTILO = """
QWidget {
    font-family: "Segoe UI";
    font-size: 13px;
    color: #333333;
}
QLabel { background: transparent; }
"""


class VentanaBienvenida(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bienvenida a La Heladeria")
        self.setFixedSize(440, 300)
        self.setStyleSheet(ESTILO + "background-color: #FFB6C1;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.addStretch(1)

        titulo = QLabel("La Heladeria")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 34px; font-weight: bold; color: #FFD700;")
        layout.addWidget(titulo)

        sub = QLabel("Los mejores sabores de la ciudad")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet("font-size: 13px; color: #800080;")
        layout.addWidget(sub)

        layout.addStretch(1)

        self.boton_entrar = QPushButton("Entrar")
        self.boton_entrar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.boton_entrar.setFixedHeight(46)
        self.boton_entrar.setStyleSheet(
            "QPushButton { background-color: #FFD700; color: #8B0050;"
            "font-size: 15px; font-weight: bold; border: none; border-radius: 12px; }"
            "QPushButton:hover { background-color: #E6C200; }"
            "QPushButton:pressed { background-color: #C9A800; }"
        )
        self.boton_entrar.clicked.connect(self.abrir_sistema)
        layout.addWidget(self.boton_entrar)

        layout.addStretch(1)

        self.ventana_sistema = None

    def abrir_sistema(self):
        self.ventana_sistema = VentanaPrincipal()
        self.ventana_sistema.show()
        self.close()


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("La Heladeria - Sistema de Pedidos")
        self.setFixedSize(600, 700)
        self.setStyleSheet(ESTILO + "background-color: #FFD700;")

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 20, 24, 18)
        layout.setSpacing(10)

        titulo = QLabel("La Heladeria")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 26px; font-weight: bold; color: #800080;")
        layout.addWidget(titulo)

        self.campo_nombre = self._crear_entrada("Escribe tu nombre...")
        self.combo_sabor = self._crear_combo(
            ["Vainilla", "Chocolate", "Fresa", "Menta", "Dulce de leche", "Frutilla"]
        )
        self.combo_topping = self._crear_combo(
            ["Ninguno", "Salsa de chocolate", "Salsa de fresa",
             "Chispas de colores", "Oreo", "Cerezas"]
        )
        self.campo_cantidad = self._crear_entrada("1")

        formulario = QFormLayout()
        formulario.setContentsMargins(0, 6, 0, 6)
        formulario.setSpacing(8)
        formulario.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        formulario.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
        formulario.addRow(self._crear_etiqueta("Nombre del cliente:"), self.campo_nombre)
        formulario.addRow(self._crear_etiqueta("Sabor del helado:"), self.combo_sabor)
        formulario.addRow(self._crear_etiqueta("Topping extra:"), self.combo_topping)
        formulario.addRow(self._crear_etiqueta("Cantidad:"), self.campo_cantidad)
        layout.addLayout(formulario)

        layout.addWidget(self._crear_etiqueta("Opciones extra:"))

        self.grupo_radios = QButtonGroup(self)
        fila_opciones = QHBoxLayout()
        fila_opciones.setContentsMargins(0, 0, 0, 0)
        fila_opciones.setSpacing(16)
        self.radio_cucurucho = self._crear_radio(fila_opciones, "Cucurucho")
        self.radio_cono = self._crear_radio(fila_opciones, "Cono")
        self.radio_nieve = self._crear_radio(fila_opciones, "Con nieve")
        layout.addLayout(fila_opciones)

        self.check_llevar = QCheckBox("Pedido para llevar")
        self.check_llevar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.check_llevar)

        layout.addWidget(self._crear_etiqueta("Observaciones:"))

        self.texto_obs = QTextEdit()
        self.texto_obs.setPlaceholderText(
            "Escribe alergias, preferencias o instrucciones especiales..."
        )
        self.texto_obs.setFixedHeight(80)
        self.texto_obs.setStyleSheet(
            "QTextEdit { background-color: white; border: 1px solid #cccccc;"
            "border-radius: 8px; padding: 6px; }"
        )
        layout.addWidget(self.texto_obs)

        fila_botones = QHBoxLayout()
        fila_botones.setSpacing(10)
        self.boton_confirmar = self._crear_boton(
            "Confirmar Pedido", "#FF69B4", self.confirmar_pedido
        )
        self.boton_limpiar = self._crear_boton("Limpiar", "#800080", self.limpiar)
        fila_botones.addWidget(self.boton_confirmar)
        fila_botones.addWidget(self.boton_limpiar)
        layout.addLayout(fila_botones)

        self.resultado = QLabel("")
        self.resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.resultado.setWordWrap(True)
        self.resultado.setMinimumHeight(52)
        self.resultado.setStyleSheet(
            "background-color: #FFB6C1; color: #800080; font-weight: bold;"
            "font-size: 13px; border-radius: 10px; padding: 8px;"
        )
        layout.addWidget(self.resultado)

        autor = QLabel("Creado por Camila Marcela")
        autor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        autor.setStyleSheet("color: #800080; font-size: 11px;")
        autor.setFont(QFont("Segoe UI", 9, QFont.Weight.Normal))
        layout.addWidget(autor)

    def _crear_etiqueta(self, texto):
        etiqueta = QLabel(texto)
        etiqueta.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        return etiqueta

    def _crear_entrada(self, placeholder):
        campo = QLineEdit()
        campo.setPlaceholderText(placeholder)
        campo.setStyleSheet(
            "QLineEdit { background-color: white; border: 1px solid #cccccc;"
            "border-radius: 8px; padding: 7px; }"
        )
        return campo

    def _crear_combo(self, valores):
        combo = QComboBox()
        combo.addItems(valores)
        combo.setStyleSheet(
            "QComboBox { background-color: white; border: 1px solid #cccccc;"
            "border-radius: 8px; padding: 6px; }"
            "QComboBox QAbstractItemView { background-color: white;"
            "selection-background-color: #FFD700; }"
        )
        return combo

    def _crear_radio(self, layout_destino, texto):
        radio = QRadioButton(texto)
        radio.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_destino.addWidget(radio)
        self.grupo_radios.addButton(radio)
        return radio

    def _crear_boton(self, texto, color, funcion):
        boton = QPushButton(texto)
        boton.setCursor(Qt.CursorShape.PointingHandCursor)
        boton.setFixedHeight(40)
        boton.setStyleSheet(
            f"QPushButton {{ background-color: {color}; color: white;"
            "font-size: 13px; font-weight: bold; border: none; border-radius: 10px; }"
            f"QPushButton:hover {{ background-color: {color}CC; }}"
        )
        boton.clicked.connect(funcion)
        return boton

    def cerrar(self):
        respuesta = QMessageBox.question(
            self,
            "Confirmar salida",
            "Seguro que quieres salir?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if respuesta == QMessageBox.StandardButton.Yes:
            self.close()

    def confirmar_pedido(self):
        nombre = self.campo_nombre.text().strip()
        if not nombre:
            self.resultado.setText("Por favor escribe tu nombre.")
            return

        cantidad = self.campo_cantidad.text().strip() or "1"
        if not cantidad.isdigit() or int(cantidad) < 1:
            self.resultado.setText("La cantidad debe ser un numero mayor a 0.")
            return

        sabor = self.combo_sabor.currentText()
        topping = self.combo_topping.currentText()

        radio = self.grupo_radios.checkedButton()
        extras = radio.text() if radio is not None else "Ninguno"

        para_llevar = "Si" if self.check_llevar.isChecked() else "No"
        observaciones = self.texto_obs.toPlainText().strip() or "Sin observaciones"

        QMessageBox.information(
            self,
            "Pedido Confirmado",
            f"Cliente: {nombre}\n"
            f"Sabor: {sabor}\n"
            f"Topping: {topping}\n"
            f"Cantidad: {cantidad}\n"
            f"Extras: {extras}\n"
            f"Para llevar: {para_llevar}\n"
            f"Observaciones: {observaciones}",
        )

        self.resultado.setText(f"Pedido listo para {nombre} - {sabor} x{cantidad}")

    def _deseleccionar_radios(self):
        self.grupo_radios.setExclusive(False)
        for boton in self.grupo_radios.buttons():
            boton.setChecked(False)
        self.grupo_radios.setExclusive(True)

    def limpiar(self):
        self.campo_nombre.clear()
        self.combo_sabor.setCurrentIndex(0)
        self.combo_topping.setCurrentIndex(0)
        self.campo_cantidad.clear()
        self._deseleccionar_radios()
        self.check_llevar.setChecked(False)
        self.texto_obs.clear()
        self.resultado.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaBienvenida()
    ventana.show()
    sys.exit(app.exec())
