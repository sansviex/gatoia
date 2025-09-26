# Agente Inteligente: Gato Doméstico

## Objetivo

Este proyecto simula el comportamiento de un **gato doméstico como agente inteligente**, utilizando **IA basada en agentes**. El gato percibe su entorno, evalúa su estado interno (hambre, sed, energía, estrés), toma decisiones racionales y actúa en consecuencia.

La simulación se desarrolla como un **juego estilo Snake** en **Python con Pygame**.

---

## Estructura del código

### 1. Librerías utilizadas

- `pygame`: simulación gráfica.
- `random`: generación de movimientos/objetos aleatorios.
- `math`: operaciones matemáticas (distancia, normalización).
- `enum`: definición de estados y tipos de objetos.
- `collections.deque`: historial de posiciones.
- `numpy`: cálculos numéricos (opcional).

### 2. Constantes principales

- **Ventana:** `WINDOW_WIDTH`, `WINDOW_HEIGHT`.
- **Grilla:** `GRID_SIZE`, `CELL_SIZE`.
- **Panel lateral:** `INFO_PANEL_WIDTH`.
- **Colores** para objetos y estados.

### 3. Enumeraciones

- **EstadoMental:** Explorando, Cazando, Comiendo, Descansando, Huyendo, Buscando refugio, Comunicando.
- **TipoObjeto:** Comida, Agua, Refugio, Juguete, Humano, Depredador, Presa, Obstáculo.

### 4. Clases principales

#### `ObjetoEntorno`

Representa un elemento del entorno (ej: comida, agua, depredador).

- Atributos: posición `(x,y)`, tipo, valor, estado activo.
- Método `dibujar()`: representa gráficamente el objeto.

#### `AgenteGato`

Simula al gato como agente inteligente.

- **Estados internos:** energía, hambre, sed, estrés, comodidad, supervivencia.
- **Sensores:** visión, olfato, oído.
- **Actuadores:** movimiento, maullido, interacción.
- **Memoria:** guarda ubicación de objetos.

Métodos clave:
- `percibir_entorno()`: usa sensores.
- `evaluar_estado()`: determina necesidades.
- `tomar_decision()`: selecciona acción.
- `huir()`, `cazar()`, `buscar_refugio()`, `descansar()`, `explorar()`, `comer()`: acciones específicas.
- `actualizar_necesidades()`: ajusta variables internas.
- `interactuar_con_objetos()`: efectos de la interacción.
- `dibujar()`: renderiza el gato.

#### `SimulacionGato`

Controla la simulación global.

- Genera el entorno (`generar_entorno`).
- Regenera recursos (`regenerar_recursos`).
- Dibuja grilla, panel y leyenda.
- Maneja eventos del usuario (pausar, reiniciar, salir).
- Método `ejecutar()`: bucle principal → percibir, decidir, actuar, dibujar.

---

## Ciclo del agente

Cada frame el gato sigue este flujo:

1. **Percibir entorno** (vista, olfato, oído).
2. **Evaluar estado interno** (hambre, sed, energía, estrés).
3. **Decidir acción** (reglas IF-THEN).
4. **Ejecutar acción** (movimiento, comer, descansar, huir, etc.).
5. **Actualizar necesidades + memoria**.
6. **Repetir ciclo**.

---

## Ejemplo de reglas IF–THEN

- Si percibe **depredador** → **huir**.
- Si **hambre > 70** y hay comida → **mover hacia comida**.
- Si **sed > 70** y hay agua → **mover hacia agua**.
- Si **energía < 20** → **descansar** en refugio.
- Si no hay necesidades urgentes → **explorar**.

---

## Controles

- **ESPACIO** → Pausar.
- **R** → Reiniciar.
- **ESC** → Salir.

---

## Panel de información

Muestra en tiempo real:

- Estado actual del gato.
- Energía, hambre, sed, estrés, comodidad, supervivencia.
- Objetos detectados con distancia.
- Tiempo de simulación y memoria.
- Naturaleza del entorno: Parcialmente observable, estocástico, dinámico.

---

## Conclusión

Este proyecto integra conceptos de IA:

- **PEAS (Performance, Environment, Actuators, Sensors).**
- **Agente racional**: maximiza supervivencia.
- **Entorno parcialmente observable, estocástico y dinámico.**
- **Agente basado en modelo**: recuerda lo que percibe y lo usa en decisiones.

---

## Ejecución

```bash
python simulacion_gato.py
