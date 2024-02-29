library(yaml)
library(data.table)

here::i_am("src/process_colors_serieA.R")
gitdir <- here::here()
gitdir.data <- file.path(gitdir, "data")

tmp <- yaml.load_file(file.path(gitdir.data, "seriea_colors.yaml"))

# write helper function to read doc and produce ...
