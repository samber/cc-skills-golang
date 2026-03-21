# Visualizing the Dependency Graph

## go mod graph (Built-in)

```bash
go mod graph
```

Output: each line contains two space-separated fields (module and its requirement) in `path@version` format:

```
example.com/main github.com/pkg/errors@v0.9.1
example.com/main golang.org/x/text@v0.3.7
github.com/pkg/errors@v0.9.1 golang.org/x/sys@v0.0.0-20210615035016
```

## go mod why

```bash
go mod why -m github.com/some/module
```

Shows the shortest import path from your code to the module — useful for understanding why an unexpected dependency exists.

## Generate a Graph Image with modgraphviz

```bash
go install golang.org/x/exp/cmd/modgraphviz@latest
go mod graph | modgraphviz | dot -Tpng -o deps.png
```

Green nodes represent versions selected by MVS (in the final build list). Grey nodes are versions that exist in the requirement graph but are not used.

## Interactive Visualization with go-mod-graph

[go-mod-graph](https://github.com/samber/go-mod-graph) provides a web-based interactive dependency explorer at [go-mod-graph.samber.dev](https://go-mod-graph.samber.dev):

- Zoomable, navigable dependency graph
- Module weight display with color-coded size indicators
- Searchable module list
- Direct links to pkg.go.dev documentation
- MVS algorithm visualization

## Complementary Analysis

```bash
# General graph queries on go mod graph output
go install golang.org/x/tools/cmd/digraph@latest
go mod graph | digraph reverse github.com/some/module
```
