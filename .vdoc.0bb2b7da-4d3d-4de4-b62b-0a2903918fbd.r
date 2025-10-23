#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# Importación de todas las librerías usadas durante el informe y breve descripcion
library(readr) # Libreria para poder importar los datos desde un csv.
library(ggplot2) # Libreria para poder hacer gráficos.
library(DT) # Libreria para poder visualizar dataframes en qmd de manera interactiva.
library(hms) # Libreria para poder tratar datos referentes a horas, minutos y segundos.
library(dplyr) # Libreria para poder manipular dataframes.
library(ggplot2) # Libreria para poder hacer gráficos.
library(tidyr) # Libreria para poder transformar dataframes.
library(e1071) # para skewness() y kurtosis()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
resultadosTokyo2025 <- read_csv(
  "data/Maraton_Tokyo/marathon_tokyo_results_2025.csv",
  col_types = cols(
    BIB = col_integer(),
    Nombre = col_character(),
    Nacionalidad = col_character(),
    Genero = col_character(),
    Edad = col_integer(),
    tiempo_oficial = col_time(format = "%H:%M:%S"),
    parcial_5km = col_time(format = "%H:%M:%S"),
    parcial_10km = col_time(format = "%H:%M:%S"),
    parcial_15km = col_time(format = "%H:%M:%S"),
    parcial_20km = col_time(format = "%H:%M:%S"),
    medio_maraton = col_time(format = "%H:%M:%S"),
    parcial_25km = col_time(format = "%H:%M:%S"),
    parcial_30km = col_time(format = "%H:%M:%S"),
    parcial_35km = col_time(format = "%H:%M:%S"),
    parcial_40km = col_time(format = "%H:%M:%S")
  ),
  quote = "\""
)

# Transformacion a formato dataframe.
resultadosTokyo2025 <- as.data.frame(resultadosTokyo2025)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# Lo visualizamos con la libreria DT porque es más interactiva a la hora de generar el documento qmd.
datatable(
  resultadosTokyo2025,
  options = list(
    pageLength = 1, # cuántas filas mostrar
    scrollX = TRUE, # habilita scroll horizontal si la fila es muy ancha
    dom = 't' # solo muestra la tabla sin paginación ni búsqueda
  ),
  rownames = FALSE # quitar número de fila en la tabla
)

#
#
#
#
#
#
#
filas <- nrow(resultadosTokyo2025)
columnas <- ncol(resultadosTokyo2025)
cat(
  "El dataframe resultadosTokyo2025 contiene",
  filas,
  "filas y",
  columnas,
  "columnas."
)
# Elimino el número de filas y columnas con el objetivo de no sobrecargar el environment.
rm(filas, columnas)
#
#
#
#
#
#
#Estadísticas de Edad
resumen_edad <- data.frame(
    Minimo = min(resultadosTokyo2025$Edad, na.rm = TRUE),
    Maximo = max(resultadosTokyo2025$Edad, na.rm = TRUE),
    Media = round(mean(resultadosTokyo2025$Edad, na.rm = TRUE),2),
    Nulos = sum(is.na(resultadosTokyo2025$Edad))
)
resumen_edad
#
#
#
#Estadísticas tiempo
cols_tiempo <- c("tiempo_oficial", "parcial_5km", "parcial_10km", "parcial_15km", "parcial_20km", "medio_maraton", "parcial_25km", "parcial_30km", "parcial_35km", "parcial_40km")

resultadosTokyo2025[cols_tiempo] <- lapply(resultadosTokyo2025[cols_tiempo], as_hms) #columnas a tipo hms

resumen_tiempos <- data.frame(
  Minimo = sapply(resultadosTokyo2025[cols_tiempo], min, na.rm = TRUE),
  Maximo = sapply(resultadosTokyo2025[cols_tiempo], max, na.rm = TRUE),
  Media  = sapply(resultadosTokyo2025[cols_tiempo], function(x) round(mean(x, na.rm = TRUE), 2)),
  Nulos  = sapply(resultadosTokyo2025[cols_tiempo], function(x) sum(is.na(x)))
)
resumen_tiempos
#
#
#
#Estadísticas tiempos en hms
resumen_tiempos_convertidos <- data.frame (
  Minimo_hms = resumen_tiempos$Minimo <- as_hms((resumen_tiempos$Minimo)),
  Maximo_hms = resumen_tiempos$Maximo <- as_hms((resumen_tiempos$Maximo)),
  Media_hms = resumen_tiempos$Media <- as_hms((resumen_tiempos$Media)),
  Nulos  = sapply(resultadosTokyo2025[cols_tiempo], function(x) sum(is.na(x)))
)
resumen_tiempos_convertidos
#
#
#
#
#
#
#
#
#
#
#Filas con NA
filas_con_na <- resultadosTokyo2025[ rowSums(is.na(resultadosTokyo2025[cols_tiempo])) > 0, ]
which(is.na(resultadosTokyo2025[cols_tiempo]), arr.ind = TRUE)

#Filas con NA en cada columna
filas_con_na <- resultadosTokyo2025[rowSums(is.na(resultadosTokyo2025[cols_tiempo])) > 0, ]
head(filas_con_na, 20)

filas_con_na <- as.data.frame(filas_con_na)
str(filas_con_na)
#
#
#
#
#
df_trabajo <- resultadosTokyo2025
```
#
cols_tiempo <- c("parcial_5km", "parcial_10km", "parcial_15km", "parcial_20km", "medio_maraton", "parcial_25km", "parcial_30km", "parcial_35km", "parcial_40km")

filas_con_na <- df_trabajo[rowSums(is.na(df_trabajo[, cols_tiempo])) > 0, ]
filas_con_na$n_na <- rowSums(is.na(filas_con_na[, cols_tiempo]))

head(filas_con_na[, c(cols_tiempo, "n_na")])
#
#
#
#
#
#
#
#
#
trabajo_df <- resultadosTokyo2025
```
#
filas_con_na$max_na_consec <- sapply(1:nrow(filas_con_na), function(i) {
  elems <- unlist(filas_con_na[i, cols_tiempo])
  na_vec <- is.na(elems)
  if(all(!na_vec)) return(0)
  max(rle(na_vec)$lengths[rle(na_vec)$values == TRUE])
})
#
#
#
# Clasificar filas
filas_con_na$clasificacion <- ifelse(
  filas_con_na$max_na_consec >= 2,
  "descartar",
  "imputable"
)
# Columna de descarte y filas a imputar
filas_con_na$descarte <- filas_con_na$clasificacion == "descartar"
filas_para_imputar <- filas_con_na[filas_con_na$descarte == FALSE, ]
#
#
#
#
#
#
#
#
#
#
#
#
#
#
trabajo_df <- resultadosTokyo2025
#
#
#
library(hms)

# --- 1. Columnas de tiempo
cols_tiempo <- c("parcial_5km", "parcial_10km", "parcial_15km", "parcial_20km", "medio_maraton", "parcial_25km", "parcial_30km", "parcial_35km", "parcial_40km")

# --- 2. Distancias acumuladas (en km)
dist <- c(5, 10, 15, 20, 21.0975, 25, 30, 35, 40)

# --- 3. Función de imputación lineal (con medio_maraton)
imputar_parciales <- function(tiempos, dist, cols_tiempo) {
  
  if (!inherits(tiempos, "hms")) tiempos <- hms::as_hms(tiempos)
  
  idx_medio <- which(cols_tiempo == "medio_maraton")
  cols_excluir <- c("parcial_5km", "parcial_40km")
  idx_excluir <- which(cols_tiempo %in% cols_excluir)

  for (i in seq_along(tiempos)) {
    if (i %in% idx_excluir) next
    if (is.na(tiempos[i])) {

      # Índice previo no NA
      prev_idx <- max(which(!is.na(tiempos[1:(i-1)])), na.rm = TRUE)
      while(prev_idx %in% idx_excluir) {
        prev_idx <- max(which(!is.na(tiempos[1:(prev_idx-1)])), na.rm = TRUE)
        if(length(prev_idx) == 0) { prev_idx <- NA; break }
      }

      # Índice posterior no NA
      next_idx <- min(which(!is.na(tiempos[(i+1):length(tiempos)])), na.rm = TRUE)
      if(is.finite(next_idx)) next_idx <- next_idx + i
      while(next_idx %in% idx_excluir) {
        next_idx <- min(which(!is.na(tiempos[(next_idx+1):length(tiempos)])), na.rm = TRUE) + next_idx
        if(next_idx > length(tiempos)) { next_idx <- NA; break }
      }

      # Interpolación lineal
      if (!is.na(prev_idx) && !is.na(next_idx)) {
        t_prev <- tiempos[prev_idx]
        t_next <- tiempos[next_idx]
        d_prev <- dist[prev_idx]
        d_next <- dist[next_idx]
        d_missing <- dist[i]

        #if (i == idx_medio) {
          # Caso especial medio_maraton: usar distancia real
          tiempos[i] <- t_prev + (d_missing - d_prev)/(d_next - d_prev) * (t_next - t_prev)
        } else {
          # Parciales normales
          tiempos[i] <- t_prev + (t_next - t_prev) * ((d_missing - d_prev)/(d_next - d_prev))
        }
      }
    }
  }
  return(tiempos)
}
#
#
#
fila_test <- filas_para_imputar[1, cols_tiempo]
print(fila_test)
imputar_parciales(fila_test, dist, cols_tiempo)

#
#
#
primera_imputacion <- as.data.frame(
  t(apply(filas_para_imputar[cols_tiempo], 1, imputar_parciales,
          dist = dist, cols_tiempo = cols_tiempo))
)

colnames(primera_imputacion) <- cols_tiempo

primera_imputacion[cols_tiempo] <- lapply(
  primera_imputacion[cols_tiempo], hms::as_hms
)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
cols_tiempo <- c("parcial_5km", "parcial_10km", "parcial_15km", "parcial_20km", "medio_maraton", "parcial_25km", "parcial_30km", "parcial_35km", "parcial_40km")

dist <- c(5, 10, 15, 20, 21.0975, 25, 30, 35, 40)

# Aplicar imputación por fila
filas_para_imputar_imputacion1 <- as.data.frame(
  t(apply(filas_para_imputar[cols_tiempo], 1, imputar_parciales,
          dist = dist, cols_tiempo = cols_tiempo))
)

filas_para_imputar_imputacion1 <- as.data.frame(
  t(apply(filas_para_imputar[cols_tiempo], 1, imputar_parciales,
          dist = dist, cols_tiempo = cols_tiempo))
)

# Restaurar nombres de columnas
colnames(filas_para_imputar_imputacion1) <- cols_tiempo

# Ahora sí podemos convertir a hms
filas_para_imputar_imputacion1[cols_tiempo] <- lapply(
  filas_para_imputar_imputacion1[cols_tiempo], hms::as_hms
)
#
#
#
#
#
cols_para_duplicados <- c(cols_tiempo, "BIB")
valores_unicos <- lapply(trabajo_df[cols_para_duplicados], unique)
valores_unicos
#
#
#
#Valores únicos por columna
n_unicos <- sapply(valores_unicos, length)

# Número de filas total
n_filas <- nrow(trabajo_df)

# Comprobar si hay duplicados
for(col in names(n_unicos)){
  if(n_unicos[col] == n_filas){
    message(paste("Columna", col, ": Ningún valor duplicado"))
  } else {
    message(paste("Columna", col, "tiene duplicados"))
  }
}
#
#
#
#
#
# Crear un data frame vacío para guardar los duplicados
duplicados_df <- data.frame(
  columna = character(),
  valor = character(),
  frecuencia = integer(),
  stringsAsFactors = FALSE
)

# Recorrer las columnas de tiempo
for (col in cols_tiempo) {
  freq <- table(trabajo_df[[col]])           # frecuencia de cada valor
  duplicados <- freq[freq > 1]               # solo los que aparecen más de una vez
  
  if (length(duplicados) > 0) {
    temp <- data.frame(
      columna = col,
      valor = names(duplicados),
      frecuencia = as.integer(duplicados),
      stringsAsFactors = FALSE
    )
    duplicados_df <- rbind(duplicados_df, temp)
  }
}

# Mostrar el resultado
duplicados_df

#
#
#
for(col in cols_tiempo){
  freq <- table(trabajo_df[[col]])  # cuenta cuántas veces aparece cada valor
  duplicados <- freq[freq > 1]               # filtra solo los que aparecen más de una vez
  if(length(duplicados) > 0){
    cat("\nColumna:", col, "\n")
    print(duplicados)
  } else {
    cat("\nColumna:", col, "→ Ningún duplicado\n")
  }
}
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
df_seconds <- resultadosTokyo2025 %>%
  mutate(
    across(
      matches("^tiempo_oficial$|^parcial_\\d+km$|^medio_maraton$"),
      ~ as.numeric(.x)
    )
  )

# Vista previa
glimpse(df_seconds)
#
#
#
#
#
#
#
#
#
#
#
# Fun. moda que devuelve el valor más frecuente (si hay empates devuelve el primero)
moda <- function(x) {
  x <- x[!is.na(x)]
  if (length(x) == 0) return(NA_real_)
  ux <- unique(x)
  ux[which.max(tabulate(match(x, ux)))]
}

# Estadísticos resumidos (redondeados)
edad_stats <- df_seconds %>%
  summarise(
    n = sum(!is.na(Edad)),
    n_missing = sum(is.na(Edad)),
    media = round(mean(Edad, na.rm = TRUE), 2),
    mediana = median(Edad, na.rm = TRUE),
    moda = moda(Edad),
  )

datatable(
  edad_stats,
  options = list(dom = 't'),
  rownames = FALSE
)

#
#
#
#
#

# Valores para líneas en los gráficos
mu <- edad_stats$media
med <- edad_stats$mediana
mod <- edad_stats$moda

p_hist <- ggplot(df_seconds, aes(x = Edad)) +
  geom_histogram(aes(y = ..density..), bins = 30, fill = "#90CAF9", color = "gray30") +
  geom_density(fill = "#1976D2", alpha = 0.15) +
  geom_vline(xintercept = mu, color = "#D32F2F", size = 1, linetype = "solid") +
  geom_vline(xintercept = med, color = "#F9A825", size = 1, linetype = "dashed") +
  geom_vline(xintercept = mod, color = "#2E7D32", size = 1, linetype = "dotdash") +
  annotate("text", x = mu, y = Inf, label = paste0("Media: ", mu), vjust = 2.2, color = "#D32F2F", size = 3.5) +
  annotate("text", x = med, y = Inf, label = paste0("Mediana: ", med), vjust = 3.8, color = "#F9A825", size = 3.5) +
  annotate("text", x = mod, y = Inf, label = paste0("Moda: ", mod), vjust = 5.4, color = "#2E7D32", size = 3.5) +
  labs(title = "Distribución de Edad (histograma + densidad)",
       x = "Edad (años)", y = "Densidad") +
  theme_minimal(base_size = 12)

p_hist
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
