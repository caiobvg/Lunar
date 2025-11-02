# src/ui/components/hardware_graphs.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QBrush, QPolygonF, QLinearGradient

class MiniGraphWidget(QWidget):
    def __init__(self, parent=None, max_points=30):
        super().__init__(parent)
        self.max_points = max_points
        self.data_points = [0.0] * self.max_points
        self.graph_color = QColor("#50E3C2") # Cor padrão
        self.setFixedSize(100, 40)

        # O "zoom" vertical mínimo que você sugeriu
        self.MIN_VERTICAL_RANGE = 20.0

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
        """Desenha o gráfico com scaling suave baseado na média móvel."""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            w = self.width()
            h = self.height()

            if not self.data_points:
                return

            # --- 1. Lógica de Scaling Suave (Baseada na Média) ---

            # Calcular a média dos dados atuais
            data_avg = sum(self.data_points) / len(self.data_points)

            # Definir a janela de 20% centralizada na média
            half_range = self.MIN_VERTICAL_RANGE / 2.0
            graph_min = data_avg - half_range
            graph_max = data_avg + half_range

            # --- 2. Clamping (Travar a escala entre 0 e 100) ---

            # Se o máximo estourou 100, desce a janela
            if graph_max > 100.0:
                overshoot = graph_max - 100.0
                graph_max = 100.0
                graph_min -= overshoot

            # Se o mínimo estourou 0, sobe a janela
            if graph_min < 0.0:
                overshoot = 0.0 - graph_min
                graph_min = 0.0
                graph_max += overshoot

            # Clamp final (se o range original for > 100, o que não deve acontecer)
            if graph_max > 100.0: graph_max = 100.0


            # --- 3. Normalização e Cálculo do Polígono ---

            # Garantir que o range nunca seja zero (evita divisão por zero)
            current_range = graph_max - graph_min
            if current_range == 0:
                current_range = 100.0 # Se for tudo 0, usa 0-100
                graph_min = 0.0

            polygon = QPolygonF()
            polygon.append(QPointF(0, h)) # Canto inferior esquerdo

            step_x = w / (self.max_points - 1)

            for i, value in enumerate(self.data_points):
                # Normalizar o valor (0-1) usando a nova escala
                normalized_y = (value - graph_min) / current_range

                # Clamp de segurança (caso o ponto saia da escala no momento da transição)
                if normalized_y < 0.0: normalized_y = 0.0
                if normalized_y > 1.0: normalized_y = 1.0

                # Inverter (Y=0 é o topo)
                y = h - (normalized_y * h)
                x = i * step_x
                polygon.append(QPointF(x, y))

            polygon.append(QPointF(w, h)) # Canto inferior direito

            # --- 4. Desenhar o Gradiente (Preenchimento) ---
            gradient = QLinearGradient(0, 0, 0, h)
            gradient.setColorAt(0, self.graph_color.lighter(120))
            gradient.setColorAt(1, QColor(0, 0, 0, 0)) # Transparente

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawPolygon(polygon)

            # --- 5. Desenhar a Linha (Contorno) ---
            line_polygon = QPolygonF(polygon)
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
