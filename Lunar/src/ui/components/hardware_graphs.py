# src/ui/components/hardware_graphs.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPolygonF, QLinearGradient

class MiniGraphWidget(QWidget):
    def __init__(self, parent=None, max_points=30):
        super().__init__(parent)
        self.max_points = max_points
        self.data_points = [0.0] * self.max_points
        self.graph_color = QColor("#50E3C2") # Cor padrão (verde-água)
        self.setFixedSize(100, 40) # Tamanho fixo para o gráfico

    def set_color(self, color_hex):
        """Define a cor principal do gráfico."""
        self.graph_color = QColor(color_hex)
        self.update()

    def add_data_point(self, value):
        """Adiciona um novo ponto de dado (0 a 100) e atualiza o gráfico."""
        if value < 0: value = 0
        if value > 100: value = 100

        self.data_points.append(value)

        while len(self.data_points) > self.max_points:
            self.data_points.pop(0)

        self.update() # Solicita o redesenho

    def paintEvent(self, event):
        """Desenha o gráfico."""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            w = self.width()
            h = self.height()

            if not self.data_points:
                return

            # Calcular os pontos para o polígono
            polygon = QPolygonF()

            # Ponto inicial (canto inferior esquerdo) para o preenchimento
            polygon.append(QPointF(0, h))

            step_x = w / (self.max_points - 1)

            for i, value in enumerate(self.data_points):
                # Normaliza o valor (0-100) para a altura do widget (h)
                # Invertemos (h - ...) pois Y=0 é o topo
                y = h - (value / 100.0) * h
                x = i * step_x
                polygon.append(QPointF(x, y))

            # Ponto final (canto inferior direito) para o preenchimento
            polygon.append(QPointF(w, h))

            # --- 1. Desenhar o Gradiente (Preenchimento) ---
            gradient = QLinearGradient(0, 0, 0, h)
            gradient.setColorAt(0, self.graph_color.lighter(120))
            gradient.setColorAt(1, QColor(0, 0, 0, 0)) # Transparente

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawPolygon(polygon)

            # --- 2. Desenhar a Linha (Contorno) ---
            # Criar uma cópia explícita do polígono
            line_polygon = QPolygonF(polygon)

            # Remove os pontos de baixo para desenhar apenas a linha superior
            line_polygon.remove(0) # Remove canto inferior esquerdo
            line_polygon.remove(line_polygon.count() - 1) # Remove canto inferior direito

            pen = painter.pen()
            pen.setColor(self.graph_color)
            pen.setWidthF(1.5)
            painter.setBrush(Qt.NoBrush)
            painter.setPen(pen)

            painter.drawPolyline(line_polygon)

        except Exception as e:
            print(f"Erro no paintEvent do MiniGraph: {e}")
