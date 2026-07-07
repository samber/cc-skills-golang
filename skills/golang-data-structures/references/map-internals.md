# Map Internals Deep Dive

## Hash Table Structure

Go maps are hash tables. Since Go 1.24 the built-in map is implemented as a Swiss Table (based on Abseil's design); earlier releases used a bucket array with overflow chains. The map header holds:

- `count` — number of entries
- a directory of tables, each holding one or more groups
- each group holds 8 slots plus a 64-bit control word (one control byte per slot) for fast probing

Each group holds 8 key-value slots. Keys and values are stored in separate arrays within a group to minimize padding waste. Collisions are resolved by open addressing (probing within and across groups), not by overflow chains.

## Memory Growth and Capacity

- **Load factor threshold**: growth triggers near a 7/8 per-group max load (`maxAvgGroupLoad`), the sweet spot between memory efficiency and probe length
- **Open addressing, no overflow chains**: a full group probes forward instead of chaining, so no single chain can degrade O(1)→O(n)
- **Table splitting**: when a table fills it splits into two tables in the directory, rather than doubling one global bucket array
- **Incremental growth**: splits happen per-table, so a single insert never rehashes the whole map, avoiding large GC pauses
- **No `cap()` function**: Capacity depends on hash distribution and load factor, not a fixed limit. Preallocation (`make(map[string]int, expectedSize)`) is worthwhile for large maps to avoid repeated growth cycles

## Preallocation

```go
// Without preallocation — multiple growths as entries are added
m := map[string]int{}

// With preallocation — allocates enough buckets upfront
m := make(map[string]int, expectedSize)
```

Preallocation avoids repeated growths. The hint is approximate — Go allocates enough groups to hold about `hint` entries before the 7/8 load factor forces a split.

## Pointers vs Values

For large value types, storing pointers reduces copy overhead:

```go
// Large struct — copied on every read/write
m := map[string]BigStruct{}  // copies large struct

// Pointer — only pointer is copied
m := map[string]*BigStruct{} // copies 8-byte pointer
```

Trade-off: pointer maps add GC pressure. For small structs (< 128 bytes), value maps are typically faster.

## `maps` Package (Go 1.21+)

| Function | Description |
| --- | --- |
| `Clone`, `Equal`, `EqualFunc` | Shallow copy and equality comparison |
| `Keys`, `Values`, `All` (1.23+) | Iterators over keys, values, or pairs |
| `Collect`, `Insert` (1.23+) | Build maps from iterators or insert entries |

See `samber/cc-skills-golang@golang-safety` skill for `Clone`, `Equal`, and sorted iteration patterns.

## Map Key Requirements

Map keys must be comparable (`==` must work). This includes:

- All numeric types, `string`, `bool`
- Pointers, channels, interfaces (compared by identity)
- Arrays of comparable types
- Structs where all fields are comparable

Slices, maps, and functions **cannot** be map keys.
