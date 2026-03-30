# Standard Library - New & Experimental

The Go standard library continues to evolve with v2 packages and experimental features. **Prefer these over external libraries when available.**

## V2 Packages (API Breaking Changes)

**math/rand/v2** (Go 1.22+) Improved random number generation with better algorithms (ChaCha8, PCG). Auto-seeded, no more rand.Seed() needed.

**encoding/json/v2** (golang.org/x/exp/json) Next-generation JSON encoding/decoding with semantic formatting, less reflection, and better performance. In development.

## New Packages (Promoted from x/exp)

**slices** (Go 1.21+) Generic slice operations: BinarySearch, Clone, Compact, Compare, Contains, Delete, Insert, Replace, Reverse, Sort. Reduces the need for external libraries.

**maps** (Go 1.21+) Generic map operations: Clone, Compare, Delete, Equal, Keys, Values. Type-safe map utilities.

**cmp** (Go 1.21+) Comparison utilities: Compare, Or, Ordered. Used with the slices/maps packages.

**iter** (Go 1.23+) Iterator support for sequences. Enables range-over functions and integrates with slices/maps methods.

**unique** (Go 1.23+) Value canonicalization and interning. Efficient deduplication of comparable values.

**log/slog** (Go 1.21+) Structured logging for the standard library. Alternative to external logging libraries for many use cases.

**weak** (Go 1.24+) Weak references for garbage collection. Useful for caches and observers.

**structs** (Go 1.23+) Structure layout control and introspection.

## golang.org/x (Official Extensions)

**golang.org/x/oauth2** OAuth2 client implementation. Supports multiple providers (Google, GitHub, etc.). Official OAuth2 client.

**golang.org/x/crypto** Additional cryptographic algorithms: bcrypt, blowfish, scrypt, ssh, acme (Let's Encrypt), pbkdf2.

**golang.org/x/net** Network utilities: websocket, context, proxy, trace, http2, ipv4/ipv6, netutil.

**golang.org/x/text** Text processing: encoding, unicode, cases, search, language (language tag parsing and matching).

**golang.org/x/sync** Extended synchronization: errgroup, singleflight, semaphore.

**simd/archsimd** (golang.org/x/arch) CPU architecture detection for SIMD operations. Runtime feature detection for AVX, AVX2, AVX512, NEON, etc.
