empty2na <- function(x){
    if(!is.character(x)) return(x)
    x[ x=="" ] <- NA_character_
    return(x)
}

remove_til_firstspace <- function(x){
    gsub("^.* ", "", x)
}

remove_last_word <- function(x){
    gsub("^(.*) .*", "\\1", x)
}

ggsave2 <- function(p, file, w=20, h=20, u="cm",...){

    stopifnot(file == basename(file))
    file <- file.path(gitdir.figures, file)
    ggsave(filename=file, plot=p, width=w, height=h,  units=u, ...)
    cmd <- sprintf(
        "%s %s &",
        fifelse(file %like% "png$", "gthumb", "zathura"),
        file)
    return(cmd)
}

read_players <- function(path) {
    dplayers <- fread(path, fill=TRUE)
    dplayers <- subset(dplayers, !(V1 %like% 'TABLE') & ! (V1 == '#') & ! V2=="")
    names(dplayers) <- c("N", "Ruolo", "Nome", "Squadra", "FVM", "Quotazione")
    .split <- function(x){
        x <- gsub(" |)", "", x)
        x <- gsub("\\(", "-", x)
        list(
            v1= gsub("^(.*)-(.*)$", "\\1",x),
            v2=gsub("^(.*)-(.*)$", "\\2",x)
        )
    }

    tmp_ruolo = dplayers[, .split(Ruolo)]
    tmp_fvm = dplayers[, .split(FVM)]
    tmp_quot = dplayers[, .split(Quotazione)]

    dplayers[, Reparto := tmp_ruolo$v1 ]
    dplayers[, Ruolo  := tmp_ruolo$v2 ]
    dplayers[, FVM  := tmp_fvm$v1 ]
    dplayers[, FVM2 := tmp_fvm$v2 ]
    dplayers[, QUOT  := tmp_quot$v1]
    dplayers[, QUOT2 := tmp_quot$v2]
    dplayers[, Quotazione := NULL ]

    # I don't know what FVM2 and QUOT2 are, let us just remove them for now
    dplayers[, FVM2 := NULL]
    dplayers[, QUOT2 := NULL]

    dplayers[, FVM := as.numeric(FVM)]
    dplayers[, QUOT := as.numeric(FVM)]

    # solo cognomi
    dplayers[ Nome %like% '\\.', Nome := sub("^(.*) .*$", "\\1", Nome ) ]

    # column names in english
    setnames(dplayers, 
        c("Nome", "Squadra"),
        c("Player", "Team"),
    )

    dplayers[, Team := fix_team_names(Team)]

    return(dplayers)
}

read_dexpgoals <- function(path=path_expgoals22){
    dexpgoals <- fread(path_expgoals22, drop = "№")
    dexpgoals <- dexpgoals[, lapply(.SD, empty2na)]
    dexpgoals <- subset(dexpgoals, !is.na(Player))
    dexpgoals[ , Player:=remove_til_firstspace(Player)]
    dexpgoals[ Team %like%  ',', Team := gsub("^.*, ", "", Team)]

    cols <- c("xG", "xA")
    .f <- function(x) {
        mean <- sub("^(.*)-(.*)$", "\\1", x)
        mean <- sub("^(.*)\\+(.*)$", "\\1", mean)
        var <- sub("^(.*)-(.*)$", "\\2", x)
        var <- sub("^(.*)\\+(.*)$", "\\2", var)
        mean <- as.numeric(mean)
        var <- as.numeric(var)
        data.table(mean, var)
    }
    tmp <- dexpgoals[, lapply(.SD, .f), .SDcols = cols]
    dexpgoals <- cbind(dexpgoals, tmp)
    set(dexpgoals, j = cols, value = NULL)
    
    dexpgoals[, Team := fix_team_names(Team)]

    return(dexpgoals)
}

load_palette <- function(path=path_colors){

    .f <- function(x){
        data.table(
            primary=gsub("^(.*),(.*)$","\\1",x),
            secondary=gsub("^(.*),(.*)$","\\2",x)
        )
    }
    tmp <- yaml::yaml.load_file(path_colors) |>
        lapply(.f) |>
        rbindlist(idcol="Team")

    palette_colors1 <<- with(tmp, setNames(primary, Team))
    palette_colors2 <<- with(tmp, setNames(secondary, Team))
    return(tmp)
}


dict_roles <- c(
    `A` = 'Attack',
    `D` = 'Defense',
    `C` = 'Midfield',
    `P` = 'Goalkeeper',
    `a` = 'Attack',
    `d` = 'Defense',
    `c` = 'Midfield',
    `p` = 'Goalkeeper',
    `ATT` = 'Attack',
    `DIF` = 'Defense',
    `CEN` = 'Midfield',
    `TRQ` = 'Midfield',
    `POR` = 'Goalkeeper',
    `Attack` = 'Attack',
    `Defense` = 'Defense',
    `Midfield` = 'Midfield',
    `Goalkeeper` = 'Goalkeeper'
)

fix_team_names <- function(x){
    dict <- c(
        `AC Milan`="Milan"
    )
    pos <- x %in% names(dict)
    x[pos]  <- dict[x[pos]]
    return(x)
}

geom_point_by_teamcolor <- function(){
    list(
        geom_point( aes(color = Team, fill = Team), size = 3, stroke = 1, shape=22),
        scale_fill_manual(values = palette_colors1),
        scale_color_manual(values = palette_colors2)
    )
}

geom_label_player <- function(repel){
    f <- if(repel==TRUE){
        ggrepel::geom_label_repel
    }else{
        geom_label
    }
    list(
        f(aes(label=Player, color=Team, fill=Team),alpha=.8),
        scale_fill_manual(values = palette_colors1),
        scale_color_manual(values = palette_colors2)
    )
}

geom_label_name <- function(repel){
    f <- if(repel==TRUE){
        ggrepel::geom_label_repel
    }else{
        geom_label
    }
    list(
        f(aes(label=name, color=Team, fill=Team),alpha=.8),
        scale_fill_manual(values = palette_colors1),
        scale_color_manual(values = palette_colors2)
    )
}


point_rules <- list(
    goal_score = 3,
    penalty_scored = 2,
    assist = 1,
    ammonizione = -.5,
    espulsione = -1
)

read_fanta <- function(path=file.path(gitdir.data, "giocatori_excel.xls"), skills=FALSE){

    .read <- if(path %like% '.xls$'){
        read_xls
    }else if(path %like% '.csv$'){
        fread
    }

    tmp <- .read(path) |>
        setDT() |>
        set(j=c('ID', "Consigliato prossima giornata", "Gol previsti", "Assist previsti", "Trend"), value=NULL)

    tmp[, Nome := remove_last_word(Nome) |> 
        tolower() |>
        stringr::str_to_title()
    ]

    tmp <- tmp[, lapply(.SD, function(x){x[x=="nd"] <- NA; x})]

    tmp[ `Nuovo acquisto` == TRUE]

    # take an average for presenze previste
    tmp[, `Presenze previste` := gsub(
        pattern="+|-",
        replacement="", 
        x=`Presenze previste`) |>
        stringr::str_split(pattern="/") |> 
        unlist() |>
        as.integer() |>
        mean()
    ]

    if( ! skills ){
        select <- c(
            `Player`="Nome",
            `Team`="Squadra",
            `role`="Ruolo",
            `score`="Punteggio",
            `appearances`="Presenze campionato corrente",
            `FM`="Fanta Media 2022-2023",
            `FM_over_tot`="FM su tot gare 2022-2023",
            `investment`="Buon investimento",
            `injured`="Infortunato",
            `injury_res`="Resistenza infortuni",
            `new`="Nuovo acquisto"
        )
    }else{
        select <- c( 
            `Player`="Nome",
            `Team`="Squadra",
            `role`="Ruolo",
            `skills`="Skills"
        )
    }
    tmp <- subset(tmp, select=select) |> 
        setnames(select, names(select))
    tmp[, role := dict_roles[role]]

    if(skills){
        skills_dt <- tmp
        tmp <- skills_dt[, unique(skills)]
        tmp <- gsub(pattern="\\[|\\]|'", replacement="", x=tmp)
        unique_skills <- stringr::str_split(tmp, ",") |> unlist() |> unique()
        unique_skills <- gsub("^ ", "", unique_skills)
        set(skills_dt, j=unique_skills, value=FALSE)
        for (skill in unique_skills){
            set(skills_dt, j=skill, i=which(skills_dt$skill %like% skill), value=TRUE)
        }
        skills_dt[, skills := FALSE]
        tmp <- skills_dt
    }
    return(tmp)
}

plot_players <- function(df=fanta, x,y, repel=FALSE){
    x <- enexpr(x); y <- enexpr(y)
    x_label <- deparse(substitute(x))
    y_label <- deparse(substitute(y))

    ggplot(df, aes(x=eval(x), y=eval(y))) + 
        geom_label_player(repel=repel) +
        facet_wrap(~role, labeller=labeller(role=dict_roles), scales='free', ncol=2)  +
        labs(x=x_label, y=y_label) +
        theme_bw()
}

scarica_probabilita_titolari <- function(giocatori=giocatori_dt){

    html_formazioni <- rvest::read_html(urls$formazioni)
    out <- html_elements(html_formazioni, '.pill') |>
        html_text2() |> 
        stringr::str_split('\n') |>
        Reduce(f='rbind') |> 
        as.data.table() |>
        setnames(c("V1", "V2"), c('nome', 'prob'))


    partite <- rvest::html_elements(html_formazioni, "#match-menu .match") |> 
        html_text2()
    partite <- gsub(pattern="[0-9]| |-|\\n|:|/","",x=partite)
    partite <- data.table(
        squadra=substr(partite, start=1, stop=3),
        avversaria=substr(partite, start=4, stop=6),
        in_casa=TRUE
    )
    partite <- rbind(
        partite,
        partite[, .(
            squadra=avversaria,
            avversaria=squadra,
            in_casa=FALSE)]
    ) 

    # merge con i miei giocatori
    out <- merge(out, giocatori, by='nome', all.y=TRUE) |>
        merge(partite, by="squadra")

    # print NA probabilities
    out[is.na(prob), sprintf( "Non trovati: %s\n", paste(nome, collapse=', ')) ]

    # print probabilities
    .g <- function(x) setorder(x, -prob) |> print() 
    out[, {
        sprintf("--- %s ---\n", ruolo) |> cat()
        .g(.SD);
        cat('\n')
    } , by='ruolo']

    return(out)
}

estrai_voti_giornata <- function(giornata){
    url_voti_giornata <- sprintf("%s/2023-24/%s", urls$voti, giornata )
    html <- read_html(url_voti_giornata)
    out <- list(
        nome = html_elements(html, '.player-name') |> html_text2(),
        ruolo = html_elements(html, '.role') |> html_attr('data-value'),
        fantavoto = html_elements(html, ".player-fanta-grade") |>
            html_attr('data-value'),
        voto = html_elements(html, ".player-grade") |>
            html_attr('data-value')
    ) |> as.data.table()
}
