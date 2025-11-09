# src/ui/components/progress_button.py

from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton
from PySide6.QtCore import Qt, QTimer, Property, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen

class ProgressButton(QPushButton):
    """
    Um QPushButton customizado que exibe um anel de progresso circular
    e a porcentagem de texto quando está no modo de carregamento.
    """
    # Sinal emitido quando a simulação interna termina
    simulation_finished = Signal()

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self._loading = False
        self._progress = 0
        self._base_text = text # Salva o texto original

        # Cores do anel (você pode ajustar)
        self.progress_color = QColor("#50e3c2") # Verde/Ciano do seu tema
        self.bg_color = QColor(self.progress_color)
        self.bg_color.setAlphaF(0.2) # Cor de fundo do anel

        # Timer para simulação (apenas para este exemplo)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_simulation)

    def set_progress(self, value):
        """Define o progresso (0-100) e força o redesenho."""
        self._progress = max(0, min(100, value))
        if self._loading:
            self.setText(f"{self._progress}%")
        self.update()

    def progress(self):
        return self._progress

    # Propriedade para permitir animação (opcional)
    progress_value = Property(int, progress, set_progress)

    def start_loading(self, run_simulation=False):
        """Inicia o modo de carregamento."""
        self._loading = True
        self.setEnabled(False)
        self.set_progress(0) # Começa em 0%

        if run_simulation:
            self._timer.start(30) # Atualiza a cada 30ms

    def stop_loading(self):
        """Para o modo de carregamento e restaura o botão."""
        self._loading = False
        self.setEnabled(True)
        self._timer.stop()
        self._progress = 0
        self.setText(self._base_text) # Restaura texto original
        self.update()

    def _update_simulation(self):
        """Função interna para o timer de simulação."""
        if self._progress < 100:
            self.set_progress(self._progress + 1)
        else:
            self._timer.stop()
            # Espera 500ms e emite o sinal de finalizado
            QTimer.singleShot(500, self.simulation_finished.emit)

    def paintEvent(self, event):
        """
        Sobrescreve o evento de pintura para desenhar o anel.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Opções de estilo
        # Pega as opções de estilo padrão do botão
        opt = QStyleOptionButton()
        self.initStyleOption(opt)

        # 2. Desenha o fundo do botão
        # Isso desenha o background, bordas, etc., de acordo com o CSS
        self.style().drawControl(QStyle.CE_PushButtonBevel, opt, painter, self)

        if not self._loading:
            # 3. Se NÃO estiver carregando, apenas desenha o texto padrão
            self.style().drawControl(QStyle.CE_PushButtonLabel, opt, painter, self)
            return

        # --- SE ESTIVER CARREGANDO ---

        # 4. Desenha o anel de progresso
        h = self.height()
        # Define o diâmetro com base na altura do botão
        diameter = h * 0.7

        # Pega o retângulo onde o conteúdo (texto) é desenhado
        contents_rect = self.style().subElementRect(QStyle.SE_PushButtonContents, opt, self)

        # Cria o retângulo para o círculo, centralizado na área de conteúdo
        circle_rect = QRectF(0, 0, diameter, diameter)
        circle_rect.moveCenter(contents_rect.center())

        # Define os ângulos
        # 0 graus é às 3h. 90*16 é às 12h.
        start_angle = 90 * 16
        # Ângulo negativo para sentido horário
        span_angle = -(self._progress * 360 / 100) * 16

        # Desenha o fundo (trilha) do anel
        pen = QPen(self.bg_color, 3, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawArc(circle_rect, 0, 360 * 16)

        # Desenha o arco de progresso
        pen.setColor(self.progress_color)
        pen.setWidth(4) # Um pouco mais espesso
        pen.setCapStyle(Qt.RoundCap) # Pontas arredondadas
        painter.setPen(pen)
        painter.drawArc(circle_rect, start_angle, span_angle)

        # 5. Desenha o texto de porcentagem
        # Diz ao estilo para desenhar o texto (que já atualizamos para "X%")
        self.style().drawControl(QStyle.CE_PushButtonLabel, opt, painter, self)
