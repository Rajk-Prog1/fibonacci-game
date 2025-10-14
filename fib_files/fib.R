# Read n from environment variable or default to 40
n_env <- Sys.getenv("FIB_N")
if (n_env != "") {
  n <- as.integer(n_env)
} else {
  n <- 40
}

fib <- function(n) {
  if (n < 2) {
    return(1)
  } else {
    return(fib(n - 1) + fib(n - 2))
  }
}

sequence <- c()
start_time <- Sys.time()

for (i in 1:n) {
  val <- fib(i)
  sequence <- c(sequence, val)
  cat(i, ". fibonacci:", val, "\n")
}

elapsed <- as.numeric(difftime(Sys.time(), start_time, units = "secs"))

result <- list(
  language = "R",
  n = n,
  sequence = sequence,
  seconds = elapsed
)

jsonlite::write_json(result, "result_r.json", pretty = TRUE, auto_unbox = TRUE)


