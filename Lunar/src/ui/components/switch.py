from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Signal, Property
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class SwitchButton(QWidget):
    toggled = Signal(bool)

    def __init__(self, parent=None, width=50, height=24):
        super().__init__(parent)
        self._checked = False
        self._circle_position = 3
        self._width = width
        self._height = height

        # Animação
        self._animation = QPropertyAnimation(self, b"circle_position")
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.setFixedSize(self._width, self._height)
        self.setCursor(Qt.PointingHandCursor)

    def get_circle_position(self):
        return self._circle_position

    def set_circle_position(self, pos):
        self._circle_position = pos
        self.update()

    circle_position = Property(float, get_circle_position, set_circle_position)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(checked)
            self.animate_switch(checked)

    def animate_switch(self, checked):
        start = 3
        end = self._width - 21  # width - (circle diameter + margin)
        if not checked:
            start, end = end, start

        self._animation.setStartValue(start)
        self._animation.setEndValue(end)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fundo do switch
        if self._checked:
            bg_color = QColor("#4a90e2")  # Azul quando ativo
            border_color = QColor("#357abd")
        else:
            bg_color = QColor("#333333")  # Cinza quando inativo
            border_color = QColor("#555555")

        # Desenhar fundo
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(0, 0, self._width, self._height, self._height // 2, self._height // 2)

        # Círculo deslizante
        circle_color = QColor("#ffffff")
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(circle_color))
        painter.drawEllipse(int(self._circle_position), 3, 18, 18)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)
