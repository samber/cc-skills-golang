# Domain-Driven Design (DDD) in Go

## Table of Contents

- [When to Use](#when-to-use)
- [Building Blocks](#building-blocks)
- [Project Structure](#project-structure)
- [Code Examples](#code-examples)
  - [Value Object — Money](#value-object--money)
  - [Aggregate Root — Order](#aggregate-root--order)
  - [Repository Interface — defined in domain](#repository-interface--defined-in-domain)
  - [Application Service — orchestrates a use case](#application-service--orchestrates-a-use-case)
- [Bounded Contexts](#bounded-contexts)
- [Wiring](#wiring)

## When to Use

Apply DDD when the business domain is complex enough that the code structure should mirror the business model — typically services with 5K+ lines, multiple bounded contexts, or rich business rules. Do NOT use for simple CRUD apps or CLI tools.

## Building Blocks

| Concept | Go Mapping | Purpose |
| --- | --- | --- |
| **Entity** | Struct with identity field | Has unique ID, mutable state, lifecycle |
| **Value Object** | Immutable struct, compared by value | No identity — represents a measurement, quantity, or descriptor |
| **Aggregate** | Entity + child entities/value objects | Consistency boundary — all mutations go through the root |
| **Repository** | Interface in domain, impl in infrastructure | Persistence abstraction for aggregates |
| **Domain Service** | Function or struct in domain package | Logic that spans multiple aggregates |
| **Domain Event** | Struct describing a fact that happened | Decouples bounded contexts |

## Project Structure

Organize by **bounded context**, grouping domain, application, and adapters vertically. This scales across multiple contexts and clarifies ownership.

```
order-service/
├── cmd/
│   └── server/
│       └── main.go                  # Wiring only
├── internal/
│   ├── order/                       # Bounded context: Order
│   │   ├── domain/
│   │   │   ├── order.go             # Order aggregate root
│   │   │   ├── item.go              # OrderItem entity
│   │   │   ├── status.go            # OrderStatus enum
│   │   │   ├── repository.go        # OrderRepository interface
│   │   │   └── events.go            # OrderPlaced, OrderShipped events
│   │   ├── application/
│   │   │   ├── place_order.go       # PlaceOrderHandler (command)
│   │   │   └── get_order.go         # GetOrderHandler (query)
│   │   └── adapters/
│   │       ├── persistence/
│   │       │   └── postgres.go      # OrderRepository implementation
│   │       └── http/
│   │           └── handler.go       # HTTP transport
│   ├── billing/                     # Bounded context: Billing (another example)
│   │   ├── domain/
│   │   ├── application/
│   │   └── adapters/
│   ├── shared/
│   │   └── money.go                 # Value object reused across contexts
│   └── events/
│       └── publisher.go             # Shared event bus (infrastructure)
├── go.mod
└── go.sum
```

**Key principles:**

- Group each bounded context **vertically** (domain → application → adapters), not by technical role
- Use `adapters/` instead of `infrastructure/` to be explicit about Hexagonal Architecture
- Make cross-context boundaries explicit (see **Bounded Contexts** section below)
- Place shared infrastructure (event bus, logging) at `internal/{shared}/` or `internal/events/`

## Code Examples

### Value Object — Money

```go
// internal/domain/shared/money.go
package shared

type Money struct {
    amount   int64  // cents — avoids float precision issues
    currency string
}

func NewMoney(amount int64, currency string) (Money, error) {
    if currency == "" {
        return Money{}, errors.New("currency is required")
    }
    return Money{amount: amount, currency: currency}, nil
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, fmt.Errorf("cannot add %s to %s", other.currency, m.currency)
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}
```

### Aggregate Root — Order

```go
// internal/domain/order/order.go
package order

type Order struct {
    id     string
    items  []Item
    status Status
    total  shared.Money
}

func NewOrder(id string) *Order {
    return &Order{id: id, status: StatusDraft}
}

// All mutations go through the aggregate root
func (o *Order) AddItem(item Item) error {
    if o.status != StatusDraft {
        return ErrOrderNotEditable
    }
    o.items = append(o.items, item)
    return o.recalculateTotal()
}

func (o *Order) Place() (OrderPlaced, error) {
    if len(o.items) == 0 {
        return OrderPlaced{}, ErrEmptyOrder
    }
    o.status = StatusPlaced
    return OrderPlaced{OrderID: o.id, Total: o.total}, nil
}
```

### Repository Interface — defined in domain

```go
// internal/order/domain/repository.go
package domain

type Repository interface {
    Save(ctx context.Context, order *Order) error
    FindByID(ctx context.Context, id string) (*Order, error)
}
```

The implementation lives in `internal/order/adapters/persistence/postgres.go` and depends on the domain — never the reverse.

### Application Service — orchestrates a use case

```go
// internal/order/application/place_order.go
package application

import (
    "context"
    "fmt"

    "myapp/internal/order/domain"
)

type PlaceOrderHandler struct {
    orders domain.Repository
    events EventPublisher
}

func (h *PlaceOrderHandler) Handle(ctx context.Context, cmd PlaceOrderCommand) error {
    order, err := h.orders.FindByID(ctx, cmd.OrderID)
    if err != nil {
        return fmt.Errorf("finding order: %w", err)
    }

    evt, err := order.Place()
    if err != nil {
        return fmt.Errorf("placing order: %w", err)
    }

    if err := h.orders.Save(ctx, order); err != nil {
        return fmt.Errorf("saving order: %w", err)
    }

    return h.events.Publish(ctx, evt)
}
```

## Bounded Contexts

Each bounded context maps to a top-level package under `internal/` with its own domain, application, and adapters. Contexts communicate through domain events or explicit anti-corruption layers — never by importing each other's internal types directly.

**Anti-corruption layer example:** If `billing/` needs to consume an `order.OrderPlaced` event, translate it to a billing-specific type:

```go
// internal/billing/adapters/events/order_events.go
package events

import (
    "myapp/internal/events"
    "myapp/internal/billing/domain"
)

type OrderPlacedSubscriber struct {
    invoices domain.InvoiceRepository
}

// Receives order.OrderPlaced, translates to billing domain
func (s *OrderPlacedSubscriber) OnOrderPlaced(evt events.OrderPlaced) error {
    // Translate and create invoice
    return s.invoices.Create(evt.OrderID, evt.Total)
}
```

This prevents billing from depending on order's internal types.

For large systems, each context can be its own Go module in a workspace (`go.work`). See the `samber/cc-skills-golang@golang-project-layout` skill for workspace setup.

## Wiring

Wire dependencies in `cmd/server/main.go` using manual constructor injection. → See `samber/cc-skills-golang@golang-dependency-injection` skill for DI library alternatives.
