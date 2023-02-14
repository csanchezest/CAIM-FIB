library(igraph)

# Load graph
# To load the graph, you need to specify your path in the following variable
path <- "/dades/cristian.sanchez.estape/CAIM/Lab6/edges.txt"

g <- read.graph(path, format="edgelist")
g <- as.undirected(g)
# plot(g, layout=layout.circle, vertex.size=3)
plot(g, layout=layout.circle, vertex.label=NA, vertex.size=3)

# 1.
V(g)
E(g)
diameter(g, directed=FALSE)
transitivity(g, type="undirected")

# check if graph g follows the power-law
d <- degree.distribution(g)
d <- table(d)
d <- as.data.frame(d)
d$d <- as.numeric(levels(d$d))[d$d]
d$d
d$d <- trunc(d$d*10^2)/10^2
plot(x=d$d, y=d$Freq, type="p", xlab="node degree", ylab="number of nodes", pch=19, main="Nº of nodes against node degree")

sizes <- page.rank(g)$vector
plot(g, vertex.size=sizes*100)

# 2
wc <- edge.betweenness.community(g)

t <- table(membership(wc))
t

barplot(t)

plot(wc, g)

dendPlot(wc)
