#!/bin/Rscript

# Scarica le probabilita di titolarita per ogni calciatore da 
# https://www.fantacalcio.it/probabili-formazioni-serie-a

suppressPackageStartupMessages({
    library(data.table)
    library(rvest)
    library(ggplot2) 
    library(geomtextpath)
})

here::i_am('src/dati_settimanali.R')
gitdir <- here::here()
gitdir.data <- file.path(gitdir, 'data')
source(file.path(gitdir, "R/paths.R"))
load_palette()


path_colors <- file.path(gitdir.data, "seriea_colors.yaml")
dplayers <- read_players(file.path(gitdir.data, "giocatori_fantacalcio.csv"))


########
# Main #
########

tmp <- yaml::read_yaml(path_my_team)
giocatori <- names(tmp)
tmp <- lapply(tmp, as.data.table) 
names(tmp) <- giocatori
giocatori_dt <- rbindlist(tmp, use.names=TRUE, idcol="nome")

abbreviazioni_squadre <- c(
    "Ata" = "Atalanta",
    "Bol" = "Bologna",
    "Cag" = "Cagliari",
    "Emp" = "Empoli",
    "Fio" = "Fiorentina",
    "Fro" = "Frosinone",
    "Gen" = "Genoa",
    "Int" = "Inter",
    "Juv" = "Juventus",
    "Laz" = "Lazio",
    "Lec" = "Lecce",
    "Mil" = "Milan",
    "Mon" = "Monza",
    "Nap" = "Napoli",
    "Rom" = "Roma",
    "Sal" = "Salernitana",
    "Sas" = "Sassuolo",
    "Udi" = "Udinese",
    "Ver" = "Verona"
)

# I miei giocatori:


tmp <- scarica_probabilita_titolari()

dvoti <- lapply(1:38, estrai_voti_giornata) |>
    rbindlist(idcol = 'giornata')

cols <- c('voto', 'fantavoto')
dvoti[, (cols) := lapply(
    .SD, function(x) sub(',', '.', x) |> as.numeric() ),
    .SDcols=cols]
# solve voti such as 55, 65
dvoti[ voto > 50, voto := voto / 10]
dvoti[ fantavoto > 50, fantavoto := fantavoto / 10]
# only select one type of votes, the first one
N_VOTO <- 2
dvoti <- dvoti[, .SD[N_VOTO], by=.(nome, giornata)]

# subset
dplot <- subset(dvoti, 
    nome %in% giocatori_dt$nome &
    giornata >= max(giornata) - 4
)

dplot <- merge(dplot, dplayers, by.x='nome', by.y='Player', all.x=TRUE)
dplot[is.na(Team), Team := "Inter"]


pd <- position_dodge(0.4)
ggplot(dplot, aes(x=giornata, y=fantavoto, group=nome, color=Team, fill=Team)) + 
    geom_point(position=pd) +
    geom_labelpath(aes(label=nome), hjust=1, alpha=.4, position=pd) +
    # geom_text() +
    facet_grid( ruolo ~ ., labeller=labeller(ruolo=dict_roles) ) +
    scale_fill_manual(values = palette_colors1) +
    scale_color_manual(values = palette_colors2) +
    theme_minimal()  +
    theme(legend.position='none') 

# ggplot(dvoti, aes(x = giornata, y=fantavoto)) + 
#     geom_label_player(repel=FALSE) +
#     theme_minimal() + 
#     NULL
