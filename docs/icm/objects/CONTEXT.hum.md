# Objects — Monorepo Noun Library

One job: route a change request to a durable component card. Cards cite the source that owns the component; this folder does not restate implementation behavior.

## Inputs

- Catalog: [`../CLAUDE.md`](../CLAUDE.md)
- Schema: [`../_meta/schema.md`](../_meta/schema.md)
- Index: [`_index.md`](_index.md)

## Process

1. Select a card by the editor’s question, not by broad directory crawling.
2. Confirm its cited source before relying on a `verified` statement.
3. Read the card’s **Hits** and **Does not hit** fields before changing source.
4. If no card fits, add a `stub` index entry before inventing a new cluster.

## Outputs

- A selected object card, or a clearly labeled `stub` route for a missing card.

## Human check

Confirm that the card identifies one source of truth and names a first-order impact boundary before editing.
