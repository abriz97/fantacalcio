# AIM: Gather information before the auction
# produces plots with past performances for each player.
# Could be improved but we'll see

suppressPackageStartupMessages({
    library(here)
    library(data.table)
    library(ggplot2)
    library(readxl)
    library(plotly)
})

# Paths
gitdir              <- here::here()
source("R/paths.R")

# Process data
dplayers            <- read_players(path_giocatori23)
dexpgoals           <- read_dexpgoals()
dpalette            <- load_palette()
fanta               <- read_fanta(path_alldata23)
skills_dt           <- read_fanta(path_alldata23, skills = TRUE)

########
# MAIN #
########

# I assume the +- are standard deviations:
ggplot(dexpgoals, aes(x = xG.mean, y = xA.mean)) +
    geom_point_by_teamcolor() +
    labs(title = "Expected Assists vs Expected Goals Season 2022/2023") +
    theme_bw()

ggplot(dexpgoals, aes(x = xG90, y = xA90)) +
    geom_point_by_teamcolor() +
    geom_label(aes(label = Player, color = Team, fill = Team), alpha = .8) +
    labs(title = "Expected Assists vs Expected Goals Season 2022/2023") +
    lims(x = c(0, 1), y = c(0, 1)) +
    theme_bw()

ggplot(dexpgoals[sample(10), ], aes(x = xG90, y = xA90)) +
    # geom_point_by_teamcolor() +
    scale_fill_manual(values = palette_colors1) +
    scale_color_manual(values = palette_colors2) +
    labs(title = "Expected Assists vs Expected Goals Season 2022/2023") +
    theme_bw()

ggplot(dexpgoals[Min > 300], aes(y = xG90 * 3 + xA90 * 1, x = Min)) +
    geom_label_player() +
    # geom_point_by_teamcolor() +
    scale_fill_manual(values = palette_colors1) +
    scale_color_manual(values = palette_colors2) +
    labs(title = "Expected Points Season 2022/2023") +
    theme_bw()


# FVM e semplicemente un tipo di valutazione...
# Fanta valore di mercato..
tmp <- merge(dplayers, dexpgoals, all.x = TRUE)
tmp[, hist(FVM)]
tmp[, xP90 := 3 * xG90 + 1 * xA90]
p <- ggplot(tmp[Min > 300], aes(x = FVM, y = xP90)) +
    geom_label_player() +
    facet_wrap(~Reparto, scales = "free", labeller = labeller(Reparto = dict_roles)) +
    labs(title = "Expected Points Season 2022/2023") +
    theme_bw() +
    theme(legend.position = "bottom") +
    guides(fill = guide_legend(nrow = 2))
cmd <- ggsave2(p = p, file = "expPvsQuotation_by_role.png", w = 30)
system(cmd)

nrow(tmp)
select_cols <- c("Player", "Team", "Titolare", "Buona Media", "Rigorista")
skills_dt <- subset(skills_dt, select = select_cols)
fanta <- merge(fanta, skills_dt)

# plot_players(fanta[Titolare == TRUE], x=investment, y=FM_over_tot)
plot_players(fanta[FM > 1 & Titolare == TRUE], x = FM, y = FM_over_tot) + geom_abline(slope = 1)
plot_players(fanta[Titolare == TRUE], x = score, y = FM_over_tot)
# plot_players(fanta[score > 70 & Titolare == TRUE], x=score, y=investment, repel=TRUE)
# plot_players(fanta[Titolare == TRUE & score > 60], x=FM_over_tot, y=investment, repel=TRUE)

# investment doesn't really make sense to me. Maybe consider score instead.
p <- plot_players(fanta[score > 50], x = score, y = FM_over_tot, repel = TRUE)
p <- plot_players(fanta[score > 50], x = score, y = FM, repel = TRUE)

ggplotly(p)
cmd <- ggsave2(p = p, file = "FMoverTot_vs_score.png", w = 30)
system(cmd)

p <- plot_players(fanta[role == "Attack" & Titolare == TRUE & FM > 0], x = score, y = FM, repel = TRUE)
cmd <- ggsave2(p = p, file = "FM_vs_score_gk.png", w = 30)
fanta[role == r, table(Titolare)]

for (r in fanta[, unique(role)]) {
    p <- plot_players(fanta[Titolare == TRUE & role == r], x = score, y = FM, repel = TRUE) +
        geom_hline(yintercept = 5, linetype = "dashed", alpha = .2)
    p
    q <- plot_players(fanta[Titolare == TRUE & role == r], x = x90, y = FM, repel = TRUE) +
        geom_hline(yintercept = 5, linetype = "dashed", alpha = .2)
    ggsave2(p = p, file = paste0("FM_vs_score_", r, ".png"), w = 30)
}

# 3 portieri
# 8 difensori
# 8 centrocampisti
# 6 attaccanti

fm_per_ruolo <- list(
    POR = c(35, 50),
    DIF = c(90, 100),
    CEN = c(125, 150),
    ATT = c(200, 250)
)
