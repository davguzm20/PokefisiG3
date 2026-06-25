# PokefisiG3

PokefisiG3 es un simulador de combates Pokémon donde se involucra Inteligencia Artificial para probar sus capacidades estratégicas.

## Niveles de dificultad de inteligencia artificial

- Fácil: Selección aleatoria de movimientos
- Intermedio: Selección de movimientos basado en diferencia de vida
- Avanzado: Selección de movimientos usando algoritmo Minimax en profundidad 4

## Detalles de Minimax

Minimax utiliza una función de evaluación heurística para averiguar y calificar un estado al que se llegó considerando las elecciones previas de la ia y su oponente. Está optimizado con poda alfa y beta para evitar generar opciones que no impacten en la toma de decisiones.

La función de evaluación heuristica puntua un estado según número de pokemon vivos, velocidad del pokemon en batalla, ventaja de tipos del pokemon en batalla y la diferencia de vida entre los pokemon en batalla. Cada uno de estos criterios está ponderado bajo un peso.

La naturaleza configurable de los pesos permite explorar el uso de algoritmos genéticos para obtener una configuración de pesos ideal para minimax. En contraste también se presenta una configuración de pesos manual. En este simulador Minimax puede configurarse o con los pesos manuales o con los pesos derivados del algoritmo genético.

## Restricciones

- 30 pokémons disponibles
- 4 pokémons por equipo
- Nivel fijo de 50
- Sin objetos

## Requisitos

- Python 3.14+
- pygame-ce

## Instalación

### 1. Crear entorno virtual

```cmd
python -m venv venv
```

### 2. Activar entorno virtual

```cmd
venv\Scripts\activate.bat
```

### 3. Instalar dependencias

```cmd
pip install -r requirements.txt
```

## Ejecutar

```cmd
python main.py
```

## Controles

- Flechas / Mouse: Navegar
- Enter / Z: Seleccionar
- Escape / X: Volver
