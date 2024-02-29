# Directory paths
gitdir.data       <- file.path(gitdir, "data")
gitdir.R          <- file.path(gitdir, "R")
gitdir.figures    <- file.path(gitdir, "figures")

# 
path_expgoals22   <- file.path(gitdir.data, "expectedgoals2223.csv")
path_giocatori23  <- file.path(gitdir.data, "giocatori_fantacalcio.csv")
path_alldata23    <- file.path(gitdir.data, "giocatori_230904.csv")
path_colors       <- file.path(gitdir.data, "seriea_colors.yaml")
path_my_team      <- file.path(gitdir, "lista_calciatori.yml")

# URL for useful pages
tmp <- "https://www.fantacalcio.it"
urls <- list(
    fanta = tmp,
    formazioni = file.path(tmp, 'probabili-formazioni-serie-a'),
    voti = file.path(tmp, "voti-fantacalcio-serie-a")
)
rm(tmp)


source(file.path(gitdir.R, "utils.R"))
