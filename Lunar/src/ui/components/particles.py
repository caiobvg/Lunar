import random
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient

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
    def __init__(self, parent=None, particle_count=80):
        super().__init__(parent)
        self.particles = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)  # ~60 FPS
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Inicializar partículas
        self.init_particles(particle_count)

    def init_particles(self, count):
        width = self.width() if self.width() > 0 else 800
        height = self.height() if self.height() > 0 else 600

        # Cores estelares - tons de branco e azul claro
        colors = [
            QColor(255, 255, 255),  # Branco puro
            QColor(240, 240, 255),  # Branco azulado
            QColor(255, 255, 240),  # Branco amarelado (estrelas quentes)
            QColor(220, 230, 255),  # Azul muito claro
            QColor(255, 240, 220),  # Laranja muito claro
        ]

        for _ in range(count):
            x = random.uniform(0, width)
            y = random.uniform(0, height)
            size = random.uniform(1.0, 3.0)
            color = random.choice(colors)

            # Velocidade baseada no tamanho (partículas maiores se movem mais devagar)
            base_speed = 0.3
            speed_factor = 1.0 / (size * 0.8)
            speed_x = random.uniform(-base_speed, base_speed) * speed_factor
            speed_y = random.uniform(-base_speed, base_speed) * speed_factor

            opacity = random.uniform(0.2, 0.8)

            self.particles.append(Particle(x, y, size, color, speed_x, speed_y, opacity))

    def update_particles(self):
        if not self.isVisible():
            return

        width = self.width()
        height = self.height()

        for particle in self.particles:
            # Atualizar posição
            particle.x += particle.speed_x
            particle.y += particle.speed_y

            # Efeito de fade pulsante
            particle.opacity += particle.fade_speed * particle.fade_direction
            if particle.opacity >= particle.original_opacity:
                particle.opacity = particle.original_opacity
                particle.fade_direction = -1
            elif particle.opacity <= 0.1:
                particle.opacity = 0.1
                particle.fade_direction = 1

            # Reposicionar partículas que saem da tela
            if particle.x < -10:
                particle.x = width + 10
            elif particle.x > width + 10:
                particle.x = -10

            if particle.y < -10:
                particle.y = height + 10
            elif particle.y > height + 10:
                particle.y = -10

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        for particle in self.particles:
            # Criar gradiente radial para efeito de brilho
            gradient = QRadialGradient(particle.x, particle.y, particle.size * 2)
            color = QColor(particle.color)
            color.setAlphaF(particle.opacity)
            gradient.setColorAt(0, color)
            gradient.setColorAt(1, QColor(255, 255, 255, 0))

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(QPointF(particle.x, particle.y), particle.size * 2, particle.size * 2)

            # Núcleo da partícula
            core_color = QColor(255, 255, 255)
            core_alpha = min(particle.opacity * 1.5, 1.0)  # Garantir que não exceda 1.0
            core_color.setAlphaF(core_alpha)
            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QPointF(particle.x, particle.y), particle.size * 0.5, particle.size * 0.5)

    def resizeEvent(self, event):
        # Ajustar partículas para novo tamanho
        if event.oldSize().width() > 0 and event.oldSize().height() > 0:
            scale_x = event.size().width() / event.oldSize().width()
            scale_y = event.size().height() / event.oldSize().height()

            for particle in self.particles:
                particle.x *= scale_x
                particle.y *= scale_y

        super().resizeEvent(event)
