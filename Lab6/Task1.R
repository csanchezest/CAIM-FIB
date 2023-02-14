library(igraph)

ws_graph <- watts.strogatz.game(1, 1000, 4, 0)

bc <- transitivity(ws_graph)
ba <- average.path.length(ws_graph)

i <- 1
p <- c()
c <- c()
l <- c()
for (k in 1:14)
{
  ws_graph <- watts.strogatz.game(1, 1000, 4, i)
  p <- append(p, i)
  c <- append(c, transitivity(ws_graph) / bc)
  l <- append(l, average.path.length(ws_graph) / ba)
  i <- i / 2
}

clustering_coeff <- data.frame(p,c)
clustering_coeff
shortest_path <- data.frame(p,l)
shortest_path
plot(clustering_coeff, log='x', ylab="", ylim=c(0,1))
par(new=TRUE)
plot(shortest_path, log='x', ylab="", ylim=c(0,1), pch=19)