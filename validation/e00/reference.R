# E00-R001 step 2: reference values from R packages.
#
#   Rscript validation/e00/reference.R <data_dir> <spader_R_dir> <out.json>
#
# <spader_R_dir> is the R/ directory of a clone of github.com/cran/SpadeR
# (SpadeR is archived on CRAN; its incidence functions are sourced directly).
# Exports the bundled R datasets into <data_dir> as items x runs CSVs, then
# computes reference values for every CSV there.

suppressPackageStartupMessages({
  library(iNEXT); library(vegan); library(Rcapture); library(jsonlite); library(VGAM)
})
args <- commandArgs(trailingOnly = TRUE)
data_dir <- args[1]; spader_dir <- args[2]; out_json <- args[3]
NBOOT <- 2000
set.seed(20261022)

# Unrounded copies: iNEXT::ChaoRichness and SpadeR round their printed output.
no_round <- function(f) {
  e <- new.env(parent = environment(f)); e$round <- function(x, digits = 0) x
  environment(f) <- e; f
}
spade <- new.env()
for (f in c("SpecInciModelh.R", "SpecInciiChao2.R")) sys.source(file.path(spader_dir, f), envir = spade)
ice_fun <- no_round(spade$SpecInciModelh)
ichao2_fun <- no_round(spade$SpecInciiChao2)
chao_fun <- no_round(iNEXT::ChaoRichness)
# SpadeR's iChao2 *variance* code fails when Q4 = 0; for the point estimate,
# run SpadeR's own statements up to the s_iChao2 assignment.
ichao2_est <- local({
  f <- spade$SpecInciiChao2; b <- as.list(body(f))
  stop_at <- which(vapply(b, function(e) grepl("s_iChao2 <-", paste(deparse(e), collapse = "")), TRUE))[1]
  body(f) <- as.call(c(b[1:stop_at], quote(s_iChao2)))
  f
})

# ---------------------------------------------------------------- export bundled data
write_mat <- function(X, name) {
  X <- (as.matrix(X) > 0) * 1L
  X <- X[rowSums(X) > 0, , drop = FALSE]
  colnames(X) <- paste0("r", seq_len(ncol(X)))
  write.csv(X, file.path(data_dir, paste0(name, ".csv")), row.names = FALSE, quote = FALSE)
}
expand_freq <- function(X) {
  X <- as.matrix(X); f <- X[, ncol(X)]
  X[rep(seq_len(nrow(X)), f), -ncol(X), drop = FALSE]
}
data(ciliates, package = "iNEXT")
for (n in names(ciliates)) write_mat(ciliates[[n]], paste0("iNEXT_ciliates_", n))
for (n in c("hare", "mvole")) { data(list = n, package = "Rcapture"); write_mat(get(n), paste0("Rcapture_", n)) }
for (n in c("bunting", "duck", "HIV", "lesbian", "rbvole")) {
  data(list = n, package = "Rcapture"); write_mat(expand_freq(get(n)), paste0("Rcapture_", n))
}
for (n in c("dune", "mite", "BCI")) {   # sites x species abundance -> species x sites incidence
  data(list = n, package = "vegan"); write_mat(t(get(n)), paste0("vegan_", n))
}
data(ant, package = "iNEXT")             # incidence_freq: first element is K
for (n in names(ant)) write.csv(data.frame(y = ant[[n]]),
                                file.path(data_dir, paste0("iNEXT_ant_", n, ".freq.csv")),
                                row.names = FALSE, quote = FALSE)

# ---------------------------------------------------------------- references
safe <- function(expr) tryCatch(suppressWarnings(expr), error = function(e) NA_real_)
ref_one <- function(spec, X = NULL) {
  K <- spec[1]; y <- spec[-1]; y <- y[y > 0]; S <- length(y); spec <- c(K, y)
  r <- list(K = K, S = S, U = sum(y))
  cr <- safe(as.numeric(unlist(chao_fun(spec, datatype = "incidence_freq"))))
  r$chao2 <- cr[2]; r$chao2_se <- cr[3]; r$chao2_lo <- cr[4]; r$chao2_hi <- cr[5]
  r$coverage <- safe(iNEXT:::Chat.Sam(spec, K))
  r$ext_1xK <- safe(iNEXT:::TD.m.est_inc(spec, 2 * K, 0) - S)
  r$ext_2xK <- safe(iNEXT:::TD.m.est_inc(spec, 3 * K, 0) - S)
  if (K >= 4) r$ichao2 <- safe(ichao2_est(spec, k = 10, conf = 0.95))
  if (K >= 4) r$ichao2_full <- safe(ichao2_fun(spec, k = 10, conf = 0.95)[1])
  r$ice <- safe({ invisible(capture.output(v <- ice_fun(spec, k = 10, conf = 0.95))); v[1] })
  if (!is.null(X)) {
    sp <- safe(specpool(t(X)))
    if (is.data.frame(sp)) { r$vegan_chao2 <- sp$chao; r$jack1 <- sp$jack1; r$jack2 <- sp$jack2 }
    if (K <= 12 && any(rowSums(X) > 1)) {
      mt <- safe(closedp.t(X)$results["Mt", "abundance"])
      r$darroch_mt <- mt
    }
  }
  # Bootstrap s.e. (H0b): S + extrapolated new items at 2K, and coverage at K.
  if (S > 1) {
    b <- safe(iNEXT:::iNEXT.Sam(spec, t = c(K, 2 * K), q = 0, nboot = NBOOT,
                                unconditional_var = FALSE)$size_based)
    if (is.data.frame(b)) {
      z <- qnorm(0.975)
      r$boot_se_S2K <- (b$qD.UCL[b$t == 2 * K] - b$qD[b$t == 2 * K]) / z
      r$boot_se_cov <- (b$SC.UCL[b$t == K] - b$SC[b$t == K]) / z
      r$boot_cov_clipped <- b$SC.UCL[b$t == K] >= 1
    }
  }
  r
}

out <- list()
for (f in sort(list.files(data_dir, pattern = "\\.csv$", full.names = TRUE))) {
  name <- sub("\\.csv$", "", basename(f))
  if (grepl("\\.freq$", name)) {
    out[[sub("\\.freq$", "", name)]] <- ref_one(read.csv(f)$y)
  } else {
    X <- as.matrix(read.csv(f))
    out[[name]] <- ref_one(c(ncol(X), rowSums(X)), X)
  }
  cat(name, "\n")
}
# Huggins conditional likelihood: model M0 with item covariates (all terms parallel over runs).
huggins <- list()
for (f in sort(list.files(file.path(data_dir, "huggins"), pattern = "\\.csv$", full.names = TRUE))) {
  d <- read.csv(f); ys <- grep("^y", names(d), value = TRUE); zs <- grep("^z", names(d), value = TRUE)
  fml <- as.formula(paste0("cbind(", paste(ys, collapse = ","), ") ~ ", paste(zs, collapse = "+")))
  par <- as.formula(paste("TRUE ~", paste(zs, collapse = "+")))
  fit <- vglm(fml, posbernoulli.t(parallel.t = par), data = d,
              control = vglm.control(epsilon = 1e-12, maxit = 200))
  huggins[[sub("\\.csv$", "", basename(f))]] <- list(N_hat = fit@extra$N.hat, beta = unname(coef(fit)))
  cat(basename(f), "\n")
}

meta <- list(R = R.version.string, iNEXT = as.character(packageVersion("iNEXT")),
             vegan = as.character(packageVersion("vegan")), VGAM = as.character(packageVersion("VGAM")),
             Rcapture = as.character(packageVersion("Rcapture")), nboot = NBOOT)
write(toJSON(list(meta = meta, datasets = out, huggins = huggins), auto_unbox = TRUE, digits = NA, na = "null"), out_json)
