rm(list = ls())
library(wesanderson)
library(tidyverse)
library(lubridate)

cubrebocas <- read_csv("parsed/Cubrebocas.csv") %>%
  mutate(`Fecha (dmy)` = dmy(`Fecha (dmy)`))

cubrebocas %>%
  ggplot() +
  geom_ribbon(aes(x = `Fecha (dmy)`, 
                    ymin = `Minimo uso cubrebocas`,
                    ymax = `Maximo uso cubrebocas`),
              fill = "#F37E21", alpha = 0.75) +
  geom_smooth(aes(x = `Fecha (dmy)`, y = value), 
              color = "deepskyblue4", size = 2, se = FALSE,
              data = cubrebocas %>% 
                pivot_longer(c(`Minimo uso cubrebocas`,`Maximo uso cubrebocas`))) +
  geom_hline(aes(yintercept = 0.5), linetype = "dashed") +
  annotate("label", x = ymd("2021/03/01"), y = 0.5, label = "50%") + 
  theme_classic() + 
  labs(
    x = "Fecha",
    y = "Uso de cubrebocas (%)",
    title = "Estimación del uso de mascarillas (cubrebocas) en la CDMX",
    subtitle = "Fuente: Reportes diarios de COVID-19 en https://covid19.cdmx.gob.mx/comunicacion",
    caption = "https://github.com/RodrigoZepeda/VacunadosCDMX"
  ) +
  scale_y_continuous(labels = scales::percent)
ggsave("images/Uso_de_cubrebocas.png", width = 8, height = 4, dpi = 750)
