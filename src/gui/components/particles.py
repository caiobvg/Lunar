import random
import math

class ParticleSystem:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        self.connections = []
        
    def create_particles(self, count=50):
        for _ in range(count):
            particle = {
                'x': random.uniform(0, self.width),
                'y': random.uniform(0, self.height),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'radius': random.uniform(1, 3),
                'color': random.choice(['#6b21ff', '#4a1c6d', '#2d1152', "#141425"]),
                'id': None
            }
            self.particles.append(particle)
    
    def draw_particles(self):
        for particle in self.particles:
            x1 = particle['x'] - particle['radius']
            y1 = particle['y'] - particle['radius']
            x2 = particle['x'] + particle['radius']
            y2 = particle['y'] + particle['radius']
            particle['id'] = self.canvas.create_oval(x1, y1, x2, y2, 
                                                   fill=particle['color'], 
                                                   outline="", tags="particle")
    
    def draw_connections(self):
        self.connections.clear()
        for i, p1 in enumerate(self.particles):
            for j, p2 in enumerate(self.particles[i+1:], i+1):
                distance = math.sqrt((p1['x']-p2['x'])**2 + (p1['y']-p2['y'])**2)
                if distance < 100:
                    # Use solid color instead of alpha
                    color = '#36365a'  # Solid light purple
                    line_id = self.canvas.create_line(p1['x'], p1['y'], p2['x'], p2['y'],
                                                     fill=color, width=1, tags="connection")
                    self.connections.append(line_id)
    
    def update(self):
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Bounce off edges
            if particle['x'] <= 0 or particle['x'] >= self.width:
                particle['vx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= self.height:
                particle['vy'] *= -1
            
            # Update canvas position
            if particle['id']:
                x1 = particle['x'] - particle['radius']
                y1 = particle['y'] - particle['radius']
                x2 = particle['x'] + particle['radius']
                y2 = particle['y'] + particle['radius']
                self.canvas.coords(particle['id'], x1, y1, x2, y2)