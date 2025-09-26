import pygame
import random
import math
from enum import Enum
from collections import deque
import numpy as np

# Inicialización de Pygame
pygame.init()

# Constantes
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
GRID_SIZE = 20
CELL_SIZE = WINDOW_WIDTH // (GRID_SIZE * 2)
INFO_PANEL_WIDTH = 300

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)

class EstadoMental(Enum):
    """Estados mentales del gato basados en su percepción del entorno"""
    EXPLORANDO = "Explorando"
    CAZANDO = "Cazando"
    COMIENDO = "Comiendo"
    DESCANSANDO = "Descansando"
    HUYENDO = "Huyendo"
    BUSCANDO_REFUGIO = "Buscando refugio"
    COMUNICANDO = "Comunicándose"

class TipoObjeto(Enum):
    """Tipos de objetos en el entorno"""
    COMIDA = "Comida"
    AGUA = "Agua"
    REFUGIO = "Refugio"
    JUGUETE = "Juguete"
    HUMANO = "Humano"
    DEPREDADOR = "Depredador"
    PRESA = "Presa"
    OBSTACULO = "Obstáculo"

class ObjetoEntorno:
    """Representa un objeto en el entorno del gato"""
    def __init__(self, x, y, tipo, valor_recurso=10):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.valor_recurso = valor_recurso
        self.activo = True
        
    def dibujar(self, screen, offset_x):
        if not self.activo:
            return
            
        x_pos = offset_x + self.x * CELL_SIZE
        y_pos = self.y * CELL_SIZE
        
        colors = {
            TipoObjeto.COMIDA: GREEN,
            TipoObjeto.AGUA: BLUE,
            TipoObjeto.REFUGIO: BROWN,
            TipoObjeto.JUGUETE: YELLOW,
            TipoObjeto.HUMANO: PINK,
            TipoObjeto.DEPREDADOR: RED,
            TipoObjeto.PRESA: ORANGE,
            TipoObjeto.OBSTACULO: GRAY
        }
        
        color = colors.get(self.tipo, WHITE)
        pygame.draw.rect(screen, color, (x_pos, y_pos, CELL_SIZE-2, CELL_SIZE-2))
        
        # Dibujar símbolo
        font = pygame.font.Font(None, 20)
        symbols = {
            TipoObjeto.COMIDA: "F",
            TipoObjeto.AGUA: "W",
            TipoObjeto.REFUGIO: "H",
            TipoObjeto.JUGUETE: "T",
            TipoObjeto.HUMANO: "P",
            TipoObjeto.DEPREDADOR: "D",
            TipoObjeto.PRESA: "M",
            TipoObjeto.OBSTACULO: "X"
        }
        text = font.render(symbols.get(self.tipo, "?"), True, BLACK)
        screen.blit(text, (x_pos + 5, y_pos + 5))

class AgenteGato:
    """Agente inteligente que simula un gato doméstico"""
    
    def __init__(self, x, y):
        # Posición
        self.x = x
        self.y = y
        self.historia_posiciones = deque(maxlen=50)
        
        # Medidas de rendimiento
        self.energia = 100
        self.hambre = 50
        self.sed = 50
        self.estres = 20
        self.comodidad = 70
        self.supervivencia = 100
        
        # Estado mental y memoria
        self.estado = EstadoMental.EXPLORANDO
        self.memoria = {}  # Memoria de objetos encontrados
        self.objetivo_actual = None
        self.tiempo_en_estado = 0
        
        # Sensores (rango de percepción)
        self.rango_vision = 5  # Visión nocturna
        self.rango_olfato = 3
        self.rango_auditivo = 7
        
        # Actuadores
        self.velocidad = 1
        self.puede_trepar = True
        self.maullido_cooldown = 0
        
        # Modelo del entorno (parcialmente observable)
        self.mapa_conocido = {}
        self.objetos_percibidos = []
        
    def percibir_entorno(self, objetos_entorno):
        """Sensores: percibe el entorno circundante"""
        self.objetos_percibidos = []
        
        for obj in objetos_entorno:
            if not obj.activo:
                continue
                
            distancia = math.sqrt((obj.x - self.x)**2 + (obj.y - self.y)**2)
            
            # Diferentes rangos según el tipo de sensor
            rango_percepcion = self.rango_vision
            if obj.tipo in [TipoObjeto.COMIDA, TipoObjeto.PRESA]:
                rango_percepcion = max(self.rango_vision, self.rango_olfato)
            elif obj.tipo == TipoObjeto.DEPREDADOR:
                rango_percepcion = max(self.rango_vision, self.rango_auditivo)
            
            if distancia <= rango_percepcion:
                self.objetos_percibidos.append(obj)
                # Actualizar memoria
                self.memoria[f"{obj.x},{obj.y}"] = obj
    
    def evaluar_estado(self):
        """Evalúa el estado interno y decide el comportamiento"""
        # Prioridades basadas en supervivencia
        if self.energia < 20 or self.supervivencia < 30:
            return EstadoMental.BUSCANDO_REFUGIO
        
        # Detectar amenazas
        for obj in self.objetos_percibidos:
            if obj.tipo == TipoObjeto.DEPREDADOR:
                return EstadoMental.HUYENDO
        
        # Necesidades básicas
        if self.hambre > 70:
            return EstadoMental.CAZANDO
        elif self.sed > 70:
            return EstadoMental.CAZANDO  # Buscar agua
        elif self.estres > 70:
            return EstadoMental.BUSCANDO_REFUGIO
        elif self.comodidad < 30:
            return EstadoMental.DESCANSANDO
        
        # Comportamiento exploratorio
        return EstadoMental.EXPLORANDO
    
    def tomar_decision(self):
        """Función de agente: mapea percepciones a acciones"""
        self.estado = self.evaluar_estado()
        self.tiempo_en_estado += 1
        
        # Decisiones basadas en el estado
        if self.estado == EstadoMental.HUYENDO:
            return self.huir()
        elif self.estado == EstadoMental.CAZANDO:
            return self.cazar()
        elif self.estado == EstadoMental.BUSCANDO_REFUGIO:
            return self.buscar_refugio()
        elif self.estado == EstadoMental.DESCANSANDO:
            return self.descansar()
        elif self.estado == EstadoMental.EXPLORANDO:
            return self.explorar()
        elif self.estado == EstadoMental.COMIENDO:
            return self.comer()
        
        return (0, 0)
    
    def huir(self):
        """Acción: alejarse de depredadores"""
        depredador = None
        for obj in self.objetos_percibidos:
            if obj.tipo == TipoObjeto.DEPREDADOR:
                depredador = obj
                break
        
        if depredador:
            # Calcular dirección opuesta
            dx = self.x - depredador.x
            dy = self.y - depredador.y
            if dx != 0:
                dx = dx / abs(dx)
            if dy != 0:
                dy = dy / abs(dy)
            self.estres += 5
            return (int(dx), int(dy))
        
        return self.explorar()
    
    def cazar(self):
        """Acción: buscar comida o agua"""
        objetivo = None
        distancia_min = float('inf')
        
        # Buscar el recurso más cercano
        for obj in self.objetos_percibidos:
            if (self.hambre > 70 and obj.tipo in [TipoObjeto.COMIDA, TipoObjeto.PRESA]) or \
               (self.sed > 70 and obj.tipo == TipoObjeto.AGUA):
                dist = math.sqrt((obj.x - self.x)**2 + (obj.y - self.y)**2)
                if dist < distancia_min:
                    distancia_min = dist
                    objetivo = obj
        
        if objetivo:
            self.objetivo_actual = objetivo
            return self.mover_hacia(objetivo.x, objetivo.y)
        
        # Si no hay objetivo visible, explorar basándose en memoria
        return self.explorar_con_memoria()
    
    def buscar_refugio(self):
        """Acción: buscar lugar seguro"""
        for obj in self.objetos_percibidos:
            if obj.tipo == TipoObjeto.REFUGIO:
                return self.mover_hacia(obj.x, obj.y)
        
        # Si no hay refugio, alejarse del peligro
        return self.explorar()
    
    def descansar(self):
        """Acción: recuperar energía"""
        self.energia = min(100, self.energia + 2)
        self.comodidad = min(100, self.comodidad + 3)
        self.estres = max(0, self.estres - 2)
        
        # Buscar refugio para descansar mejor
        for obj in self.objetos_percibidos:
            if obj.tipo == TipoObjeto.REFUGIO:
                return self.mover_hacia(obj.x, obj.y)
        
        return (0, 0)  # Quedarse quieto
    
    def explorar(self):
        """Acción: explorar el entorno"""
        # Movimiento aleatorio con tendencia a explorar áreas nuevas
        movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        # Preferir movimientos hacia áreas no exploradas
        mejores_movimientos = []
        for dx, dy in movimientos:
            nueva_x = self.x + dx
            nueva_y = self.y + dy
            if f"{nueva_x},{nueva_y}" not in self.mapa_conocido:
                mejores_movimientos.append((dx, dy))
        
        if mejores_movimientos:
            return random.choice(mejores_movimientos)
        
        return random.choice(movimientos)
    
    def explorar_con_memoria(self):
        """Explora usando la memoria de objetos conocidos"""
        if self.memoria:
            # Buscar recursos recordados
            for pos, obj in self.memoria.items():
                if obj.tipo in [TipoObjeto.COMIDA, TipoObjeto.AGUA]:
                    x, y = map(int, pos.split(','))
                    return self.mover_hacia(x, y)
        
        return self.explorar()
    
    def comer(self):
        """Acción: consumir recursos"""
        for obj in self.objetos_percibidos:
            if abs(obj.x - self.x) <= 1 and abs(obj.y - self.y) <= 1:
                if obj.tipo == TipoObjeto.COMIDA:
                    self.hambre = max(0, self.hambre - 30)
                    self.energia = min(100, self.energia + 20)
                    obj.activo = False
                    return (0, 0)
                elif obj.tipo == TipoObjeto.AGUA:
                    self.sed = max(0, self.sed - 30)
                    obj.activo = False
                    return (0, 0)
        
        return self.explorar()
    
    def mover_hacia(self, target_x, target_y):
        """Calcula el movimiento hacia un objetivo"""
        dx = target_x - self.x
        dy = target_y - self.y
        
        if dx != 0:
            dx = dx / abs(dx)
        if dy != 0:
            dy = dy / abs(dy)
        
        return (int(dx), int(dy))
    
    def actualizar(self, objetos_entorno):
        """Ciclo principal del agente"""
        # Percibir
        self.percibir_entorno(objetos_entorno)
        
        # Decidir
        dx, dy = self.tomar_decision()
        
        # Actuar
        nueva_x = self.x + dx * self.velocidad
        nueva_y = self.y + dy * self.velocidad
        
        # Validar movimiento
        if 0 <= nueva_x < GRID_SIZE and 0 <= nueva_y < GRID_SIZE:
            # Verificar obstáculos
            puede_mover = True
            for obj in self.objetos_percibidos:
                if obj.tipo == TipoObjeto.OBSTACULO and obj.x == nueva_x and obj.y == nueva_y:
                    puede_mover = False
                    break
            
            if puede_mover:
                self.x = nueva_x
                self.y = nueva_y
                self.historia_posiciones.append((self.x, self.y))
        
        # Actualizar estados internos
        self.actualizar_necesidades()
        
        # Verificar interacción con objetos
        self.interactuar_con_objetos()
    
    def actualizar_necesidades(self):
        """Actualiza las necesidades del gato con el tiempo"""
        self.hambre = min(100, self.hambre + 0.5)
        self.sed = min(100, self.sed + 0.7)
        self.energia = max(0, self.energia - 0.3)
        
        if self.estado == EstadoMental.EXPLORANDO:
            self.estres = max(0, self.estres - 0.2)
        
        # Calcular supervivencia general
        self.supervivencia = (self.energia + (100 - self.hambre) + (100 - self.sed) + 
                            self.comodidad + (100 - self.estres)) / 5
    
    def interactuar_con_objetos(self):
        """Interactúa con objetos cercanos"""
        for obj in self.objetos_percibidos:
            if abs(obj.x - self.x) <= 1 and abs(obj.y - self.y) <= 1:
                if obj.tipo == TipoObjeto.COMIDA and self.hambre > 50:
                    self.estado = EstadoMental.COMIENDO
                    self.comer()
                elif obj.tipo == TipoObjeto.AGUA and self.sed > 50:
                    self.estado = EstadoMental.COMIENDO
                    self.comer()
                elif obj.tipo == TipoObjeto.REFUGIO:
                    self.comodidad = min(100, self.comodidad + 5)
                    self.estres = max(0, self.estres - 3)
                elif obj.tipo == TipoObjeto.JUGUETE:
                    self.estres = max(0, self.estres - 2)
                    self.comodidad = min(100, self.comodidad + 2)
                elif obj.tipo == TipoObjeto.HUMANO:
                    if self.estres < 50:
                        self.comodidad = min(100, self.comodidad + 3)
                        self.estado = EstadoMental.COMUNICANDO
    
    def dibujar(self, screen, offset_x):
        """Dibuja el gato en la pantalla"""
        x_pos = offset_x + self.x * CELL_SIZE
        y_pos = self.y * CELL_SIZE
        
        # Color según estado
        colors = {
            EstadoMental.EXPLORANDO: (100, 100, 100),
            EstadoMental.CAZANDO: (150, 100, 50),
            EstadoMental.HUYENDO: (200, 50, 50),
            EstadoMental.DESCANSANDO: (50, 50, 150),
            EstadoMental.COMIENDO: (50, 150, 50),
            EstadoMental.BUSCANDO_REFUGIO: (150, 150, 50),
            EstadoMental.COMUNICANDO: (200, 100, 200)
        }
        
        color = colors.get(self.estado, BLACK)
        
        # Dibujar el gato
        pygame.draw.circle(screen, color, 
                         (x_pos + CELL_SIZE//2, y_pos + CELL_SIZE//2), 
                         CELL_SIZE//2 - 2)
        
        # Dibujar ojos
        pygame.draw.circle(screen, WHITE, 
                         (x_pos + CELL_SIZE//3, y_pos + CELL_SIZE//3), 2)
        pygame.draw.circle(screen, WHITE, 
                         (x_pos + 2*CELL_SIZE//3, y_pos + CELL_SIZE//3), 2)
        
        # Dibujar rango de visión (opcional)
        if False:  # Cambiar a True para debug
            pygame.draw.circle(screen, (255, 255, 0, 50), 
                             (x_pos + CELL_SIZE//2, y_pos + CELL_SIZE//2), 
                             self.rango_vision * CELL_SIZE, 1)

class SimulacionGato:
    """Clase principal para la simulación"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH + INFO_PANEL_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Simulación IA: Agente Gato Doméstico")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Inicializar agente
        self.gato = AgenteGato(GRID_SIZE//2, GRID_SIZE//2)
        
        # Inicializar entorno
        self.objetos_entorno = []
        self.generar_entorno()
        
        # Control de simulación
        self.running = True
        self.paused = False
        self.tiempo_simulacion = 0
        
    def generar_entorno(self):
        """Genera objetos aleatorios en el entorno"""
        self.objetos_entorno = []
        
        # Generar obstáculos
        for _ in range(10):
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            if (x, y) != (self.gato.x, self.gato.y):
                self.objetos_entorno.append(ObjetoEntorno(x, y, TipoObjeto.OBSTACULO))
        
        # Generar recursos
        tipos_recursos = [
            (TipoObjeto.COMIDA, 8),
            (TipoObjeto.AGUA, 5),
            (TipoObjeto.REFUGIO, 3),
            (TipoObjeto.JUGUETE, 4),
            (TipoObjeto.PRESA, 3)
        ]
        
        for tipo, cantidad in tipos_recursos:
            for _ in range(cantidad):
                x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
                if (x, y) != (self.gato.x, self.gato.y):
                    self.objetos_entorno.append(ObjetoEntorno(x, y, tipo))
        
        # Agregar humano
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        self.objetos_entorno.append(ObjetoEntorno(x, y, TipoObjeto.HUMANO))
        
        # Agregar depredador ocasional
        if random.random() > 0.7:
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            self.objetos_entorno.append(ObjetoEntorno(x, y, TipoObjeto.DEPREDADOR))
    
    def regenerar_recursos(self):
        """Regenera recursos consumidos ocasionalmente"""
        if random.random() < 0.02:  # 2% de probabilidad por frame
            tipo = random.choice([TipoObjeto.COMIDA, TipoObjeto.AGUA, TipoObjeto.PRESA])
            x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
            self.objetos_entorno.append(ObjetoEntorno(x, y, tipo))
    
    def dibujar_grilla(self):
        """Dibuja la grilla del juego"""
        for x in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (x * CELL_SIZE, 0), 
                           (x * CELL_SIZE, WINDOW_HEIGHT))
        for y in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, GRAY, 
                           (0, y * CELL_SIZE), 
                           (WINDOW_WIDTH, y * CELL_SIZE))
    
    def dibujar_panel_info(self):
        """Dibuja el panel de información"""
        panel_x = WINDOW_WIDTH
        pygame.draw.rect(self.screen, (40, 40, 40), 
                        (panel_x, 0, INFO_PANEL_WIDTH, WINDOW_HEIGHT))
        
        # Título
        title = self.font.render("AGENTE GATO IA", True, WHITE)
        self.screen.blit(title, (panel_x + 50, 20))
        
        # Estado actual
        y_offset = 70
        estado_text = self.font.render(f"Estado: {self.gato.estado.value}", True, YELLOW)
        self.screen.blit(estado_text, (panel_x + 10, y_offset))
        
        # Medidas de rendimiento
        y_offset += 40
        metrics_title = self.font.render("MEDIDAS DE RENDIMIENTO", True, WHITE)
        self.screen.blit(metrics_title, (panel_x + 10, y_offset))
        
        y_offset += 30
        metrics = [
            ("Supervivencia", self.gato.supervivencia, GREEN if self.gato.supervivencia > 50 else RED),
            ("Energía", self.gato.energia, GREEN if self.gato.energia > 50 else RED),
            ("Hambre", self.gato.hambre, RED if self.gato.hambre > 70 else GREEN),
            ("Sed", self.gato.sed, RED if self.gato.sed > 70 else GREEN),
            ("Estrés", self.gato.estres, RED if self.gato.estres > 70 else GREEN),
            ("Comodidad", self.gato.comodidad, GREEN if self.gato.comodidad > 50 else RED)
        ]
        
        for nombre, valor, color in metrics:
            text = self.small_font.render(f"{nombre}: {valor:.1f}%", True, WHITE)
            self.screen.blit(text, (panel_x + 10, y_offset))
            
            # Barra de progreso
            bar_width = 150
            bar_height = 15
            pygame.draw.rect(self.screen, GRAY, 
                           (panel_x + 120, y_offset, bar_width, bar_height))
            pygame.draw.rect(self.screen, color, 
                           (panel_x + 120, y_offset, 
                            int(bar_width * valor / 100), bar_height))
            
            y_offset += 25
        
        # Sensores activos
        y_offset += 20
        sensor_title = self.font.render("PERCEPCIONES", True, WHITE)
        self.screen.blit(sensor_title, (panel_x + 10, y_offset))
        
        y_offset += 30
        objetos_text = self.small_font.render(f"Objetos detectados: {len(self.gato.objetos_percibidos)}", 
                                             True, WHITE)
        self.screen.blit(objetos_text, (panel_x + 10, y_offset))
        
        y_offset += 25
        for obj in self.gato.objetos_percibidos[:5]:  # Mostrar máximo 5
            dist = math.sqrt((obj.x - self.gato.x)**2 + (obj.y - self.gato.y)**2)
            obj_text = self.small_font.render(f"- {obj.tipo.value} (dist: {dist:.1f})", 
                                             True, WHITE)
            self.screen.blit(obj_text, (panel_x + 20, y_offset))
            y_offset += 20
        
        # Información del entorno
        y_offset = WINDOW_HEIGHT - 150
        env_title = self.font.render("ENTORNO", True, WHITE)
        self.screen.blit(env_title, (panel_x + 10, y_offset))
        
        y_offset += 30
        env_info = [
            f"Tiempo: {self.tiempo_simulacion // 60}s",
            f"Memoria: {len(self.gato.memoria)} objetos",
            f"Tipo: Parcialmente Observable",
            f"Naturaleza: Estocástico, Dinámico"
        ]
        
        for info in env_info:
            text = self.small_font.render(info, True, WHITE)
            self.screen.blit(text, (panel_x + 10, y_offset))
            y_offset += 20
        
        # Controles
        y_offset = WINDOW_HEIGHT - 40
        controls = self.small_font.render("ESPACIO: Pausar | R: Reiniciar | ESC: Salir", 
                                         True, WHITE)
        self.screen.blit(controls, (panel_x + 10, y_offset))
    
    def dibujar_leyenda(self):
        """Dibuja la leyenda de objetos"""
        leyenda_y = WINDOW_HEIGHT - 100
        leyenda_items = [
            ("F: Comida", GREEN),
            ("W: Agua", BLUE),
            ("H: Refugio", BROWN),
            ("T: Juguete", YELLOW),
            ("P: Humano", PINK),
            ("D: Depredador", RED),
            ("M: Presa", ORANGE),
            ("X: Obstáculo", GRAY)
        ]
        
        x_offset = 10
        for texto, color in leyenda_items:
            pygame.draw.rect(self.screen, color, (x_offset, leyenda_y, 15, 15))
            text = self.small_font.render(texto, True, WHITE)
            self.screen.blit(text, (x_offset + 20, leyenda_y))
            x_offset += 120
    
    def manejar_eventos(self):
        """Maneja los eventos del usuario"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.reiniciar()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def reiniciar(self):
        """Reinicia la simulación"""
        self.gato = AgenteGato(GRID_SIZE//2, GRID_SIZE//2)
        self.generar_entorno()
        self.tiempo_simulacion = 0
    
    def ejecutar(self):
        """Bucle principal de la simulación"""
        while self.running:
            self.manejar_eventos()
            
            if not self.paused:
                # Actualizar agente
                self.gato.actualizar(self.objetos_entorno)
                
                # Regenerar recursos ocasionalmente
                self.regenerar_recursos()
                
                # Mover depredador (comportamiento simple)
                for obj in self.objetos_entorno:
                    if obj.tipo == TipoObjeto.DEPREDADOR and random.random() < 0.3:
                        obj.x = max(0, min(GRID_SIZE-1, obj.x + random.randint(-1, 1)))
                        obj.y = max(0, min(GRID_SIZE-1, obj.y + random.randint(-1, 1)))
                
                self.tiempo_simulacion += 1
            
            # Dibujar todo
            self.screen.fill(BLACK)
            self.dibujar_grilla()
            
            # Dibujar objetos del entorno
            for obj in self.objetos_entorno:
                obj.dibujar(self.screen, 0)
            
            # Dibujar agente (el gato)
            self.gato.dibujar(self.screen, 0)
            
            # Dibujar panel de información
            self.dibujar_panel_info()
            
            # Dibujar leyenda
            self.dibujar_leyenda()
            
            # Actualizar pantalla
            pygame.display.flip()
            
            # Controlar FPS
            self.clock.tick(10)  # 10 FPS para que sea fluido pero no muy rápido
if __name__ == "__main__":
    simulacion = SimulacionGato()
    simulacion.ejecutar()
    pygame.quit()

