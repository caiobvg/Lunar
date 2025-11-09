# src/ui/components/hardware_graphs.py

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import (QPainter, QColor, QBrush, QPolygonF,
                           QLinearGradient, QRadialGradient, QImage) # [NOVO] QImage

class MiniGraphWidget(QWidget):
    def __init__(self, parent=None, max_points=30):
        super().__init__(parent)
        self.max_points = max_points
        self.data_points = [0.0] * self.max_points
        self.graph_color = QColor("#50E3C2") # Cor padrão
        self.setFixedSize(100, 40)

        # O "zoom" vertical mínimo que você sugeriu
        self.MIN_VERTICAL_RANGE = 30

    def set_color(self, color_hex):
        """Define a cor principal do gráfico."""
        self.graph_color = QColor(color_hex)
        self.update()

    def add_data_point(self, value):
        """Adiciona um novo ponto de dado e atualiza o gráfico."""
        if value < 0: value = 0
        # if value > 100: value = 100  <-- [REMOVIDO]

        self.data_points.append(value)

        while len(self.data_points) > self.max_points:
            self.data_points.pop(0)

        self.update() # Solicita o redesenho

    def paintEvent(self, event):
        """Desenha o gráfico com scaling instantâneo E FADE NOS DOIS EIXOS."""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            w = self.width()
            h = self.height()

            if not self.data_points:
                return

            # --- 1. Lógica de Scaling Instantâneo (Baseado no último ponto) ---
            current_value = self.data_points[-1]
            half_range = self.MIN_VERTICAL_RANGE / 2.0
            graph_min = current_value - half_range
            graph_max = current_value + half_range

            # --- 2. Clamping (Travar a escala apenas em 0) ---
            if graph_min < 0.0:
                overshoot = 0.0 - graph_min
                graph_min = 0.0
                graph_max += overshoot

            # --- 3. Normalização e Cálculo do Polígono ---
            current_range = graph_max - graph_min
            if current_range < 0.01:
                current_range = self.MIN_VERTICAL_RANGE

            polygon = QPolygonF()
            polygon.append(QPointF(0, h)) # Canto inferior esquerdo

            line_polygon = QPolygonF() # Polígono apenas para a linha

            step_x = w / (self.max_points - 1)

            for i, value in enumerate(self.data_points):
                normalized_y = (value - graph_min) / current_range

                # Clamp de segurança
                if normalized_y < 0.0: normalized_y = 0.0
                if normalized_y > 1.0: normalized_y = 1.0

                y = h - (normalized_y * h)
                x = i * step_x

                polygon.append(QPointF(x, y))
                line_polygon.append(QPointF(x, y))

            polygon.append(QPointF(w, h)) # Canto inferior direito

            # Cores
            solid_color = QColor(self.graph_color)
            faded_color = QColor(self.graph_color)
            faded_color.setAlphaF(0.0) # 0% opaco

            # --- 4. [ALTERADO] Desenhar o Preenchimento (Fill) em um Buffer ---

            # Criar buffer off-screen para aplicar os dois gradientes
            buffer = QImage(self.size(), QImage.Format_ARGB32_Premultiplied)
            buffer.fill(Qt.transparent)

            buffer_painter = QPainter(buffer)
            buffer_painter.setRenderHint(QPainter.Antialiasing)

            # Etapa 1: Gradiente Vertical (de cima para baixo)
            v_grad = QLinearGradient(0, 0, 0, h)
            v_grad.setColorAt(0.0, solid_color.lighter(120)) # Cor no topo
            v_grad.setColorAt(1.0, faded_color) # Transparente embaixo

            buffer_painter.setPen(Qt.NoPen)
            buffer_painter.setBrush(v_grad)
            buffer_painter.drawPolygon(polygon)

            # **ETAPA 2: APLICAR FADE "EIXO X" (Esquerda E Direita)**
            buffer_painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)

            h_grad_mask = QLinearGradient(0, 0, w, 0)
            h_grad_mask.setColorAt(0.0, QColor(0,0,0,0))   # Esquerda = Transparente
            h_grad_mask.setColorAt(0.8, QColor(0,0,0,255)) # 80% = Opaco (Foco)
            h_grad_mask.setColorAt(1.0, QColor(0,0,0,0))   # Direita = Transparente

            buffer_painter.fillRect(self.rect(), h_grad_mask)
            buffer_painter.end()

            # --- 5. Desenhar o Buffer na Tela ---
            painter.drawImage(0, 0, buffer)

            # --- 6. Desenhar a Linha (com Fade Esquerda/Direita) ---
            h_grad_line = QLinearGradient(0, 0, w, 0)
            h_grad_line.setColorAt(0.0, faded_color) # Esquerda = Transparente
            h_grad_line.setColorAt(0.8, solid_color) # 80% = Sólido (Foco)
            h_grad_line.setColorAt(1.0, faded_color) # Direita = Transparente

            pen = painter.pen()
            pen.setBrush(h_grad_line)
            pen.setWidthF(1.5)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)

            painter.drawPolyline(line_polygon)

        except Exception as e:
            print(f"Erro no paintEvent do MiniGraph: {e}")
