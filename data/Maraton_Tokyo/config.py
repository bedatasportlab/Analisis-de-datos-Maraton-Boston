# Configuración para la extracción de datos del Maratón de Tokio

# ========== CONFIGURACIÓN PRINCIPAL ==========
# Cambia esta variable para elegir el modo de extracción:

MODO_EXTRACCION = "prueba_mini"  # Opciones: "prueba_mini", "prueba_extendida", "completo"

# ========== CONFIGURACIÓN DE MODOS ==========
CONFIGURACION = {
    "prueba_mini": {
        "max_pages": 1,
        "max_runners_per_page": 10,
        "descripcion": "🧪 MODO PRUEBA MINI: 1 página, 10 corredores máximo (para pruebas rápidas)"
    },
    "prueba_extendida": {
        "max_pages": 5,
        "max_runners_per_page": None,  # Todos los corredores de la página
        "descripcion": "🔬 MODO PRUEBA EXTENDIDA: 5 páginas, ~250 corredores (para validar funcionamiento)"
    },
    "completo": {
        "max_pages": None,  # Sin límite, usar total_pages
        "max_runners_per_page": None,
        "descripcion": "🚀 MODO COMPLETO: Todas las páginas, todos los corredores (extracción completa)"
    }
}

# ========== CONFIGURACIÓN DE VELOCIDAD ==========
DELAY_ENTRE_REQUESTS = 2.0  # Segundos entre cada atleta (2.0 = más conservador para evitar bloqueos)
DELAY_ENTRE_PAGINAS = 3     # Segundos extra entre páginas

# ========== CONFIGURACIÓN DE ARCHIVOS ==========
# Los archivos se guardarán automáticamente con nombres dinámicos:
# - Modo prueba: marathon_tokyo_results_2024_prueba_mini.csv
# - Modo completo: marathon_tokyo_results_2024_completo.csv

# ========== INSTRUCCIONES DE USO ==========
"""
Para cambiar el modo de extracción:

1. PRUEBA RÁPIDA (recomendado para empezar):
   MODO_EXTRACCION = "prueba_mini"
   
2. PRUEBA EXTENDIDA (para validar antes de extracción completa):
   MODO_EXTRACCION = "prueba_extendida"
   
3. EXTRACCIÓN COMPLETA (todos los datos):
   MODO_EXTRACCION = "completo"

Después de cambiar el modo, ejecuta:
python extraccion.py
"""