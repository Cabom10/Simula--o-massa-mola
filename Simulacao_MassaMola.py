import pygame
import math

# Inicialização do Pygame
pygame.init()

# Configurações de tela
width, height = 800, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulação Massa-Mola")

# Constantes físicas
k = 0.1  # Constante elástica (ajustada para deixar a mola mais macia)
dt = 0.1 # Passo de tempo
damping = 0.005 # Amortecimento
spring_segments = 20  # Número de segmentos para desenhar a mola
spring_amplitude = 1  # Amplitude da curvatura da mola
wall_padding = 20  # Espaçamento das bordas
restitution = 1  # Coeficiente de restituição

# Cores
black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
red = (255, 0, 0)

# Classe para as massas
class Mass:
    def __init__(self, x, y, m, label):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = 0
        self.mass = m
        self.radius = 20
        self.label = label
        self.dragging = False  # Para rastrear se a massa está sendo arrastada

    def update(self, springs):
        if not self.dragging:  # Só atualizar se não estiver sendo arrastada
            # Aplicar amortecimento
            self.vx *= (1 - damping)
            self.vy *= (1 - damping)
        
            # Atualizar aceleração com base nas molas conectadas
            self.ax = 0
            self.ay = 0
            for spring in springs:
                if spring.m1 == self or spring.m2 == self:
                    other = spring.m2 if spring.m1 == self else spring.m1
                    dx = other.x - self.x
                    dy = other.y - self.y
                    d = math.dist((self.x, self.y), (other.x, other.y))
                    force = k * (d - spring.rest_length)
                    self.ax += (dx / d) * force / self.mass
                    self.ay += (dy / d) * force / self.mass
        
            self.vx += self.ax * dt
            self.vy += self.ay * dt
        
            self.x += self.vx * dt
            self.y += self.vy * dt

    def draw(self, screen):
        pygame.draw.circle(screen, black, (int(self.x), int(self.y)), self.radius)
        font = pygame.font.SysFont(None, 24)
        label_text = font.render(self.label, True, black)
        screen.blit(label_text, (self.x - 10, self.y - 30))

# Classe para as molas
class Spring:
    def __init__(self, m1, m2, label):
        self.m1 = m1
        self.m2 = m2
        self.rest_length = math.dist((m1.x, m1.y), (m2.x, m2.y))
        self.label = label

    def update(self):
        dx = self.m2.x - self.m1.x
        dy = self.m2.y - self.m1.y
        d = math.dist((self.m1.x, self.m1.y), (self.m2.x, self.m2.y))
        force = k * (d - self.rest_length)
        fx = (dx / d) * force
        fy = (dy / d) * force
        
        # Aplicar força nas massas
        self.m1.ax += fx / self.m1.mass
        self.m1.ay += fy / self.m1.mass
        self.m2.ax -= fx / self.m2.mass
        self.m2.ay -= fy / self.m2.mass

    def draw(self, screen):
        # Desenhar mola curva
        segments = spring_segments
        segment_length = math.dist((self.m1.x, self.m1.y), (self.m2.x, self.m2.y)) / segments
        angle = math.atan2(self.m2.y - self.m1.y, self.m2.x - self.m1.x)
        
        x0, y0 = self.m1.x, self.m1.y
        x1, y1 = self.m2.x, self.m2.y
        
        points = []
        for i in range(segments + 1):
            t = i / segments
            x = (1 - t) * x0 + t * x1
            y = (1 - t) * y0 + t * y1
            offset = math.sin(t * math.pi * 2) * spring_amplitude
            x_offset = math.cos(angle + math.pi / 2) * offset
            y_offset = math.sin(angle + math.pi / 2) * offset
            points.append((x + x_offset, y + y_offset))
        
        pygame.draw.lines(screen, black, False, points, 2)

        # Adicionar rótulo
        mid_x = (self.m1.x + self.m2.x) / 2
        mid_y = (self.m1.y + self.m2.y) / 2
        font = pygame.font.SysFont(None, 20)
        label_text = font.render(self.label, True, black)
        screen.blit(label_text, (mid_x - 10, mid_y - 20))

def check_wall_collisions(mass):
    if mass.x < wall_padding:
        mass.x = wall_padding
        mass.vx *= -restitution
    elif mass.x > width - wall_padding:
        mass.x = width - wall_padding
        mass.vx *= -restitution
    
    if mass.y < wall_padding:
        mass.y = wall_padding
        mass.vy *= -restitution
    elif mass.y > height - wall_padding:
        mass.y = height - wall_padding
        mass.vy *= -restitution

# Função para desenhar as setas de aceleração e velocidade
def draw_arrow(screen, x, y, vx, vy, color):
    arrow_size = 5  # Ajustado para menor tamanho
    end_x = x + vx
    end_y = y + vy
    pygame.draw.line(screen, color, (x, y), (end_x, end_y), 2)  # Linha mais fina
    angle = math.atan2(vy, vx)
    pygame.draw.polygon(screen, color, [(end_x, end_y), 
                                        (end_x - arrow_size * math.cos(angle - math.pi / 6), end_y - arrow_size * math.sin(angle - math.pi / 6)),
                                        (end_x - arrow_size * math.cos(angle + math.pi / 6), end_y - arrow_size * math.sin(angle + math.pi / 6))])

# Inicialização das massas e molas
masses = [
    Mass(width / 3, height / 3, 1, 'M1'),
    Mass(2 * width / 3, height / 3, 1, 'M2'),
    Mass(width / 2, 2 * height / 3, 1, 'M3')
]

springs = [
    Spring(masses[0], masses[1], 'k1'),
    Spring(masses[1], masses[2], 'k2'),
    Spring(masses[2], masses[0], 'k3')
]

# Variáveis para rastrear o arrasto da massa
dragging_mass = None
mouse_x_offset = 0
mouse_y_offset = 0

# Loop principal
running = True
while running:
    screen.fill(white)
    
    # Verificar eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for mass in masses:
                if math.dist((mouse_x, mouse_y), (mass.x, mass.y)) < mass.radius:
                    dragging_mass = mass
                    mouse_x_offset = mouse_x - mass.x
                    mouse_y_offset = mouse_y - mass.y
                    mass.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_mass:
                dragging_mass.dragging = False
                dragging_mass = None
        elif event.type == pygame.MOUSEMOTION:
            if dragging_mass:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dragging_mass.x = mouse_x - mouse_x_offset
                dragging_mass.y = mouse_y - mouse_y_offset

    # Atualizar molas e massas
    for spring in springs:
        spring.update()
    
    for mass in masses:
        mass.update(springs)
        check_wall_collisions(mass)
    
    # Desenhar molas e massas
    for spring in springs:
        spring.draw(screen)
    
    for mass in masses:
        mass.draw(screen)
    
    # Desenhar setas de velocidade (azul) e aceleração (vermelho)
    for mass in masses:
        draw_arrow(screen, mass.x, mass.y, mass.vx * 5, mass.vy * 5, blue)  # Ajustado para menor escala
        draw_arrow(screen, mass.x, mass.y, mass.ax*5 , mass.ay *5, red)  # Ajustado para menor escala
    
    pygame.display.flip()
    pygame.time.delay(int(dt * 10))

pygame.quit()
