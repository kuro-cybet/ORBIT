from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QRadialGradient
from ui.styles import Theme
import random
import math


class Particle:
    """Represents a single data packet in the visualization"""
    
    def __init__(self, start_x, start_y, target_x, target_y, color, speed=1.0):
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.color = color
        self.progress = 0.0
        self.speed = speed
        self.size = random.uniform(2, 4)
        self.alive = True
        
    def update(self):
        """Update particle position"""
        self.progress += self.speed * 0.02
        
        if self.progress >= 1.0:
            self.alive = False
            return
            
        # Smooth easing
        t = self.progress
        ease_t = t * t * (3.0 - 2.0 * t)  # Smoothstep
        
        self.x = self.start_x + (self.target_x - self.start_x) * ease_t
        self.y = self.start_y + (self.target_y - self.start_y) * ease_t
        

class PacketFlowWidget(QWidget):
    """Animated packet flow visualization for network traffic"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 300)
        
        self.particles = []
        self.connections = []  # List of (target_x, target_y, color, count)
        
        # Center point (local machine)
        self.center_x = 0
        self.center_y = 0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(33)  # ~30 FPS
        
        # Particle spawn timer
        self.spawn_timer = QTimer(self)
        self.spawn_timer.timeout.connect(self.spawn_particles)
        self.spawn_timer.start(200)  # Spawn every 200ms
        
        self.setStyleSheet(f"""
            PacketFlowWidget {{
                background-color: {Theme.COLOR_PANEL};
                border: 1px solid {Theme.COLOR_BORDER};
                border-radius: 4px;
            }}
        """)
        
    def resizeEvent(self, event):
        """Update center point on resize"""
        super().resizeEvent(event)
        self.center_x = self.width() // 2
        self.center_y = self.height() // 2
        
    def set_connections(self, connections):
        """
        Update active connections for visualization
        connections: list of dicts with 'remote_ip', 'status', 'count'
        """
        self.connections.clear()
        
        # Convert connections to visualization targets
        angle_step = (2 * math.pi) / max(len(connections), 1)
        radius = min(self.width(), self.height()) * 0.35
        
        for i, conn in enumerate(connections[:12]):  # Limit to 12 for performance
            angle = i * angle_step
            target_x = self.center_x + radius * math.cos(angle)
            target_y = self.center_y + radius * math.sin(angle)
            
            # Color based on status
            if conn.get('status') == 'Malware':
                color = Theme.COLOR_MALWARE
            elif conn.get('status') == 'Suspicious':
                color = Theme.COLOR_SUS
            else:
                color = Theme.COLOR_CLEAN
                
            count = conn.get('count', 1)
            self.connections.append((target_x, target_y, color, count))
            
    def spawn_particles(self):
        """Spawn new particles for active connections"""
        if not self.connections:
            return
            
        for target_x, target_y, color, count in self.connections:
            # Spawn particles based on connection count (more active = more particles)
            spawn_count = min(count, 3)
            
            for _ in range(spawn_count):
                if random.random() < 0.3:  # 30% chance per connection
                    speed = random.uniform(0.8, 1.5)
                    particle = Particle(
                        self.center_x, self.center_y,
                        target_x, target_y,
                        color, speed
                    )
                    self.particles.append(particle)
                    
        # Limit total particles for performance
        if len(self.particles) > 100:
            self.particles = self.particles[-100:]
            
    def update_animation(self):
        """Update all particles and trigger repaint"""
        # Update particles
        for particle in self.particles:
            particle.update()
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p.alive]
        
        self.update()  # Trigger paintEvent
        
    def paintEvent(self, event):
        """Draw the visualization"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background grid (subtle)
        self.draw_grid(painter)
        
        # Draw center node (local machine)
        self.draw_center_node(painter)
        
        # Draw connection lines
        self.draw_connections(painter)
        
        # Draw particles
        self.draw_particles(painter)
        
    def draw_grid(self, painter):
        """Draw subtle background grid"""
        pen = QPen(QColor(Theme.COLOR_BORDER))
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Vertical lines
        for x in range(0, self.width(), 50):
            painter.drawLine(x, 0, x, self.height())
            
        # Horizontal lines
        for y in range(0, self.height(), 50):
            painter.drawLine(0, y, self.width(), y)
            
    def draw_center_node(self, painter):
        """Draw the central node representing local machine"""
        # Outer glow
        gradient = QRadialGradient(self.center_x, self.center_y, 30)
        gradient.setColorAt(0, QColor(Theme.COLOR_ACCENT + "40"))
        gradient.setColorAt(1, QColor(Theme.COLOR_ACCENT + "00"))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(self.center_x, self.center_y), 30, 30)
        
        # Core
        painter.setBrush(QBrush(QColor(Theme.COLOR_ACCENT)))
        pen = QPen(QColor(Theme.COLOR_TEXT_MAIN))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawEllipse(QPointF(self.center_x, self.center_y), 12, 12)
        
        # Label
        painter.setPen(QPen(QColor(Theme.COLOR_TEXT_MAIN)))
        painter.drawText(
            QRectF(self.center_x - 50, self.center_y + 25, 100, 20),
            Qt.AlignCenter,
            "LOCAL"
        )
        
    def draw_connections(self, painter):
        """Draw lines to connection targets"""
        for target_x, target_y, color, count in self.connections:
            pen = QPen(QColor(color + "30"))  # Semi-transparent
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(
                int(self.center_x), int(self.center_y),
                int(target_x), int(target_y)
            )
            
            # Draw target node
            painter.setBrush(QBrush(QColor(color)))
            painter.drawEllipse(QPointF(target_x, target_y), 6, 6)
            
    def draw_particles(self, painter):
        """Draw all active particles"""
        painter.setPen(Qt.NoPen)
        
        for particle in self.particles:
            # Glow effect
            gradient = QRadialGradient(particle.x, particle.y, particle.size * 2)
            gradient.setColorAt(0, QColor(particle.color))
            gradient.setColorAt(1, QColor(particle.color + "00"))
            painter.setBrush(QBrush(gradient))
            painter.drawEllipse(
                QPointF(particle.x, particle.y),
                particle.size * 2,
                particle.size * 2
            )
            
            # Core
            painter.setBrush(QBrush(QColor(particle.color)))
            painter.drawEllipse(
                QPointF(particle.x, particle.y),
                particle.size,
                particle.size
            )
