import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QBrush

class Particle:
    def __init__(self, x, y, size, color, speed_x, speed_y, opacity):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.opacity = opacity
        self.original_opacity = opacity
        self.fade_direction = random.choice([-1, 1])
        self.fade_speed = random.uniform(0.005, 0.02)

class ParticleSystem(QWidget):
    def __init__(self, parent=None, particle_count=60):
        super().__init__(parent)
        self.particles = []
        self.particle_count = particle_count
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(33)  # ~30 FPS
        
        # Configurar para ser completamente transparente
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Garantir que fique atrás de outros widgets
        self.lower()

        # Inicializar partículas apenas quando o widget for mostrado
        self.initialized = False

    def showEvent(self, event):
        """Inicializa partículas quando o widget é mostrado"""
        if not self.initialized:
            self.init_particles(self.particle_count)
            self.initialized = True
        super().showEvent(event)

    def init_particles(self, count):
        """Inicializa partículas distribuídas por toda a área"""
        width = self.width() if self.width() > 0 else 800
        height = self.height() if self.height() > 0 else 600

        # Cores mais vibrantes para serem visíveis através do header
        colors = [
            QColor(255, 255, 255),  # Branco puro
            QColor(220, 230, 255),  # Azul muito claro
            QColor(240, 240, 255),  # Branco azulado
            QColor(255, 250, 250),  # Branco levemente rosado
        ]

        self.particles = []
        for _ in range(count):
            # Distribuir partículas por toda a área
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            size = random.uniform(1.0, 3.0)  # Partículas um pouco maiores
            color = random.choice(colors)

            # Velocidades mais lentas
            speed_x = random.uniform(-0.1, 0.1)
            speed_y = random.uniform(-0.1, 0.1)

            # Opacidade mais alta para serem visíveis
            opacity = random.uniform(0.3, 0.8)

            self.particles.append(Particle(x, y, size, color, speed_x, speed_y, opacity))

    def update_particles(self):
        """Atualiza posição e estado das partículas"""
        if not self.isVisible() or not self.initialized:
            return

        width = self.width()
        height = self.height()

        if width <= 0 or height <= 0:
            return

        for particle in self.particles:
            # Atualizar posição
            particle.x += particle.speed_x
            particle.y += particle.speed_y

            # Efeito de fade pulsante
            particle.opacity += particle.fade_speed * particle.fade_direction

            # Garantir que a opacidade fique dentro dos limites válidos
            if particle.opacity >= particle.original_opacity:
                particle.opacity = particle.original_opacity
                particle.fade_direction = -1
            elif particle.opacity <= 0.1:
                particle.opacity = 0.1
                particle.fade_direction = 1

            # Reposicionar partículas que saem da tela
            if particle.x < -50:
                particle.x = width + 50
                particle.y = random.uniform(0, height)
            elif particle.x > width + 50:
                particle.x = -50
                particle.y = random.uniform(0, height)

            if particle.y < -50:
                particle.y = height + 50
                particle.x = random.uniform(0, width)
            elif particle.y > height + 50:
                particle.y = -50
                particle.x = random.uniform(0, width)

        self.update()

    def paintEvent(self, event):
        """Desenha as partículas - CORRIGIDO para evitar erros de QPainter"""
        if not self.initialized or not self.isVisible():
            return

        try:
            painter = QPainter(self)
            if not painter.isActive():
                return
                
            painter.setRenderHint(QPainter.Antialiasing)
            
            # IMPORTANTE: Não preencher o fundo - deixar transparente
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            for particle in self.particles:
                # Garantir que a opacidade esteja dentro do range válido
                opacity = max(0.05, min(1.0, particle.opacity))

                color = QColor(particle.color)
                color.setAlphaF(opacity)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(color))

                # Desenhar partícula
                painter.drawEllipse(QPointF(particle.x, particle.y), particle.size, particle.size)
                
            painter.end()
            
        except Exception as e:
            print(f"Erro no ParticleSystem paintEvent: {e}")

    def resizeEvent(self, event):
        """Reinicializa partículas quando o tamanho muda"""
        super().resizeEvent(event)
        if self.initialized and event.oldSize().width() > 0 and event.oldSize().height() > 0:
            old_width = event.oldSize().width()
            old_height = event.oldSize().height()
            new_width = event.size().width()
            new_height = event.size().height()

            scale_x = new_width / old_width
            scale_y = new_height / old_height

            for particle in self.particles:
                particle.x *= scale_x
                particle.y *= scale_y
