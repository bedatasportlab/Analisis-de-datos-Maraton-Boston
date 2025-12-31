# librerias.R
# Añade al vector las librerías que necesites, se instalarán e importarán solas en el qmd o script que estés usando.
(function(){
  libs <- c(
    "readr", "ggplot2", "DT", "hms", "dplyr", "tidyr",
    "e1071", "stringr", "knitr", "viridis", "plotly",
    "gapminder", "patchwork", "skimr", "naniar", "grid",
    "kableExtra", "caret", "rsample", "tidyverse", "factoextra", "cluster",
    "NbClust", "fpc", "magrittr", "gam", "corrplot", "mgcv", "MASS"
  )
  
  for (lib in libs) {
    if (!require(lib, character.only = TRUE)) {
      install.packages(lib, dependencies = TRUE)
      library(lib, character.only = TRUE)
    }
  }
})()