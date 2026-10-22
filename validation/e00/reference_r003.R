# E00-R003 step 2: reference values for the estimators added in R003.
#
#   Rscript validation/e00/reference_r003.R <data_dir> <out.json>
#
# <data_dir> is filled by make_synthetic.py; the bundled R datasets are
# exported here exactly as in reference.R. References:
#   - log-linear models: Rcapture::closedp.t (all 12 models) and
#     Rcapture::closedpCI.t with interaction formulas (list dependence),
#     with and without heterogeneity;
#   - generalised Chao (Boehning et al. 2013, binomial form): the logistic
#     fit by stats::glm, the estimator assembled in R from that fit;
#   - breakaway_nof1: breakaway::breakaway_nof1 on a frequency table built in R.

suppressPackageStartupMessages({
  library(Rcapture); library(jsonlite); library(breakaway); library(iNEXT); library(vegan)
})
args <- commandArgs(trailingOnly = TRUE)
data_dir <- args[1]; out_json <- args[2]
GLM_TIGHT <- list(epsilon = 1e-14, maxit = 200)   # passed through to glm()
# Rcapture's Chao.neg refits (after dropping a negative eta) call glm without
# the user's control, i.e. at glm's default epsilon = 1e-8, which leaves
# ~1e-5 relative error in the s.e. Force the tight tolerance on every fit;
# this changes convergence precision only, not the model.
local({
  orig <- get("glm.call", envir = asNamespace("Rcapture"))
  tight <- function(Y, mX., cst = NULL, ...) {
    a <- list(...); a$control <- GLM_TIGHT
    do.call(orig, c(list(Y = Y, mX. = mX., cst = cst), a))
  }
  environment(tight) <- environment()
  assignInNamespace("glm.call", tight, ns = "Rcapture")
})

# Unrounded copy: iNEXT::ChaoRichness rounds its output (as in reference.R).
no_round <- function(f) {
  e <- new.env(parent = environment(f)); e$round <- function(x, digits = 0) x
  environment(f) <- e; f
}
chao_fun <- no_round(iNEXT::ChaoRichness)

# ---------------------------------------------------------------- export bundled data (as reference.R)
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
for (n in c("dune", "mite", "BCI")) {
  data(list = n, package = "vegan"); write_mat(t(get(n)), paste0("vegan_", n))
}

safe <- function(expr) tryCatch(suppressWarnings(expr), error = function(e) NULL)
row_of <- function(tab, i) list(N = tab[i, "abundance"], se_printed = tab[i, "stderr"],
                                deviance = tab[i, "deviance"], df = tab[i, "df"],
                                aic = tab[i, "AIC"], bic = tab[i, "BIC"])

# Standard error from the Fisher information at the fitted coefficients, with
# Rcapture's own formulas. glm's vcov() uses the IRLS weights of the previous
# iterate, which leaves O(sqrt(epsilon)) error; this removes it.
se_exact <- function(g, type, t) {
  if (!inherits(g, "glm") || any(is.na(coef(g)))) return(NA)
  b <- unname(coef(g)); D <- model.matrix(g)
  V <- solve(crossprod(D * sqrt(fitted(g))))
  if (type == "Mb") {
    N <- exp(b[1]) * (1 + exp(b[3]))^t / (1 + exp(b[3]) - exp(b[2]))
    v <- N * c(1, exp(b[2]) / (1 + exp(b[3]) - exp(b[2])),
               t * exp(b[3]) / (1 + exp(b[3])) - exp(b[3]) / (1 + exp(b[3]) - exp(b[2])))
    return(sqrt(drop(t(v) %*% V %*% v) - N))
  }
  if (type == "Mbh") {
    den <- 1 + exp(b[4]) - exp(b[3])
    N <- exp(b[1]) * (1 + exp(b[4]))^(t - 1) * (1 + exp(b[2] + b[3]) / den)
    v <- exp(b[1]) * (1 + exp(b[4]))^(t - 1) * c(
      1 + exp(b[2] + b[3]) / den, exp(b[2] + b[3]) / den,
      exp(b[2] + b[3]) / den + exp(b[2] + 2 * b[3]) / den^2,
      (t - 1) * exp(b[4]) / (1 + exp(b[4])) - exp(b[2] + b[3] + b[4]) / den^2)
    return(sqrt(drop(t(v) %*% V %*% v) - N))
  }
  sqrt(exp(b[1]) + exp(2 * b[1]) * V[1, 1])
}
SHORT <- c("M0" = "M0", "Mt" = "Mt", "Mh Chao (LB)" = "MhC", "Mh Poisson2" = "MhP",
           "Mh Darroch" = "MhD", "Mh Gamma3.5" = "MhG", "Mth Chao (LB)" = "MthC",
           "Mth Poisson2" = "MthP", "Mth Darroch" = "MthD", "Mth Gamma3.5" = "MthG",
           "Mb" = "Mb", "Mbh" = "Mbh")

# Interaction designs (0-based run pairs in the JSON, as crsafety takes them).
designs <- function(K) {
  main <- paste0("c", 1:K, collapse = " + ")
  d <- list(
    list(name = "Mt+c1c2", pairs = list(c(0, 1)), h = NULL,
         f = paste("~", main, "+ c1:c2")),
    list(name = "Mt+c1c2+Chao", pairs = list(c(0, 1)), h = "Chao",
         f = paste("~", main, "+ c1:c2")),
    list(name = "Mt+c1c2+Poisson2", pairs = list(c(0, 1)), h = "Poisson",
         f = paste("~", main, "+ c1:c2")),
    list(name = "Mt+c1c2+Darroch", pairs = list(c(0, 1)), h = "Darroch",
         f = paste("~", main, "+ c1:c2")))
  if (K >= 4) d[[length(d) + 1]] <- list(
    name = "Mt+pairs123", pairs = list(c(0, 1), c(0, 2), c(1, 2)), h = NULL,
    f = paste("~", main, "+ c1:c2 + c1:c3 + c2:c3"))
  d
}

loglin <- function(X) {
  K <- ncol(X)
  out <- list()
  cp <- safe(closedp.t(X, control = GLM_TIGHT))
  if (!is.null(cp)) {
    tab <- cp$results
    for (i in rownames(tab)) out[[i]] <- c(row_of(tab, i),
      list(se = tryCatch(se_exact(cp$glm[[SHORT[[i]]]], SHORT[[i]], K), error = function(e) NA),
           eta_removed = if (i %in% c("Mh Chao (LB)", "Mth Chao (LB)")) cp$neg.eta[[SHORT[[i]]]] else NULL))
  }
  if (K >= 3) for (d in designs(K)) {
    hc <- if (identical(d$h, "Poisson")) list(theta = 2) else list()
    r <- safe(closedpCI.t(X, mX = as.formula(d$f), h = d$h, h.control = hc, control = GLM_TIGHT))
    if (!is.null(r)) out[[d$name]] <- c(row_of(r$results, 1),
                                        list(se = tryCatch(se_exact(r$fit, "loglinear", K), error = function(e) NA),
                                             pairs = d$pairs, h = if (is.null(d$h)) NA else d$h))
  }
  out
}

gen_chao <- function(y, K, Z = NULL) {
  low <- y %in% c(1, 2)
  r <- as.numeric(y[low] == 2)
  if (sum(r) == 0 || sum(r) == length(r)) return(NULL)
  off <- rep(log((K - 1) / 2), sum(low))
  fit <- if (is.null(Z)) glm(r ~ 1, family = binomial, offset = off,
                             control = glm.control(epsilon = 1e-14, maxit = 200))
         else glm(r ~ ., data = as.data.frame(Z[low, , drop = FALSE]), family = binomial,
                  offset = off, control = glm.control(epsilon = 1e-14, maxit = 200))
  theta <- exp(predict(fit, type = "link") - off)
  list(N = length(y) + sum(1 / (K * theta + K * (K - 1) / 2 * theta^2)), beta = unname(coef(fit)))
}

nof1 <- function(y) {
  tb <- table(y)
  df <- data.frame(index = as.integer(names(tb)), frequency = as.integer(tb))
  r <- safe(breakaway_nof1(df))
  if (is.null(r)) return(NULL)
  list(estimate = r$estimate, error = r$error, model = r$model,
       name = if (is.null(r$other$name)) NA else r$other$name)
}

out <- list()
for (f in sort(list.files(data_dir, pattern = "\\.csv$", full.names = TRUE))) {
  name <- sub("\\.csv$", "", basename(f))
  X <- as.matrix(read.csv(f)); K <- ncol(X); y <- rowSums(X)
  spec <- c(K, y)
  r <- list(K = K, S = nrow(X), U = sum(y))
  if (K <= 12 && any(y > 1)) r$loglinear <- loglin(X)
  if (K >= 2) {
    r$gen_chao <- gen_chao(y, K)
    ch <- safe(as.numeric(unlist(chao_fun(spec, datatype = "incidence_freq"))))
    if (!is.null(ch) && sum(y == 1) > 0 && sum(y == 2) > 0) r$inext_chao2 <- ch[2]
  }
  r$breakaway_nof1 <- nof1(y)
  out[[name]] <- r
  cat(name, "\n")
}

hug <- list()
for (f in sort(list.files(file.path(data_dir, "huggins"), pattern = "\\.csv$", full.names = TRUE))) {
  d <- read.csv(f); ys <- grep("^y", names(d)); zs <- grep("^z", names(d))
  y <- rowSums(d[, ys]); K <- length(ys)
  hug[[sub("\\.csv$", "", basename(f))]] <- gen_chao(y, K, as.matrix(d[, zs, drop = FALSE]))
  cat(basename(f), "\n")
}

meta <- list(R = R.version.string, Rcapture = as.character(packageVersion("Rcapture")),
             breakaway = as.character(packageVersion("breakaway")),
             iNEXT = as.character(packageVersion("iNEXT")))
write(toJSON(list(meta = meta, datasets = out, gen_chao_cov = hug),
             auto_unbox = TRUE, digits = NA, na = "null", null = "null"), out_json)
