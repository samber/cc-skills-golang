# Standard Library - New & Experimental

The Go standard library continues to evolve with v2 packages and experimental features. **Prefer these over external libraries when available.**

## V2 Packages (API Breaking Changes)

**math/rand/v2** (Go 1.22+) Improved random number generation with better algorithms (ChaCha8, PCG). Auto-seeded, no more rand.Seed() needed.

**encoding/json/v2** (default JSON implementation as of Go 1.27; introduced experimental behind `GOEXPERIMENT=jsonv2` in Go 1.25) Next-generation JSON encoding/decoding, now the default underneath `encoding/json`. Stricter than v1: rejects duplicate object keys and invalid UTF-8. → See `samber/cc-skills-golang@golang-modernize` skill for migration guidance and the `GOEXPERIMENT=nojsonv2` rollback.

## New Packages (Promoted from x/exp)

**slices** (Go 1.21+) Generic slice operations: BinarySearch, Clone, Compact, Compare, Contains, Delete, Insert, Replace, Reverse, Sort. Reduces the need for external libraries.

**maps** (Go 1.21+) Generic map operations: Clone, Copy, DeleteFunc, Equal, EqualFunc. Go 1.23+ adds iterator helpers such as All, Collect, Insert, Keys, and Values.

**cmp** (Go 1.21+) Comparison utilities: Compare, Or, Ordered. Used with the slices/maps packages.

**iter** (Go 1.23+) Iterator support for sequences. Enables range-over functions and integrates with slices/maps methods.

**unique** (Go 1.23+) Value canonicalization and interning. Efficient deduplication of comparable values.

**log/slog** (Go 1.21+) Structured logging for the standard library. Alternative to external logging libraries for many use cases.

**weak** (Go 1.24+) Weak references for garbage collection. Useful for caches and observers.

**structs** (Go 1.23+) Structure layout control and introspection.

**uuid** (Go 1.27+) UUID generation and parsing (`New`, `NewV4`, `NewV7`, `Parse`). Prefer over `github.com/google/uuid` for new code unless a v3/v5 namespaced UUID or another RFC-variant feature the stdlib package doesn't cover is needed.

## golang.org/x (Official Extensions)

**golang.org/x/oauth2** OAuth2 client implementation. Supports multiple providers (Google, GitHub, etc.). Official OAuth2 client.

**golang.org/x/crypto** Additional cryptographic algorithms: bcrypt, blowfish, scrypt, ssh, acme (Let's Encrypt), pbkdf2.

**golang.org/x/net** Network utilities: websocket, context, proxy, trace, http2, ipv4/ipv6, netutil.

**golang.org/x/text** Text processing: encoding, unicode, cases, search, language (language tag parsing and matching).

**golang.org/x/sync** Extended synchronization: errgroup, singleflight, semaphore.

**golang.org/x/sys/cpu** CPU feature detection for architecture-specific optimized code. Use it only when dispatching between measured implementations; prefer portable stdlib code first.
