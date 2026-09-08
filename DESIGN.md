# HedgeKnight Design System

<!-- impeccable:design-schema 1 -->

## Direction

HedgeKnight is a risk operations console. The interface makes exposure compression tangible through one decisive horizontal rail: unhedged Spot BNB occupies the full measure; a simulated short claims gold space from the left; the remaining exposure stays graphite. This mechanism leads the first viewport and persists across plan, monitor, and receipt states.

## Color

The canvas is near-black `#0B0E11`, with graphite surfaces `#111519` and `#171B20`, crisp rules `#2A2F35`, and warm primary text `#F4F0E5`. Gold `#F0B90B` marks selected controls, the protected exposure, and primary action. Green is reserved for passed policy and healthy state; amber for warnings and replay provenance; red for blocked and destructive state.

## Typography

Space Grotesk Variable carries headings and decisive tabular measurements. Manrope Variable carries navigation, controls, explanations, and dense operational content. Technical IDs and digests use monospace. Numerals remain tabular where values must align.

## Composition

Desktop uses a fixed 244px navigation rail and an open operations canvas. The Overview starts with one command heading and action, then pairs the net BNB figure with the exposure rail. Market evidence forms a ruled strip rather than a card row. Scenario controls and the evidence ledger share the lower field at unequal widths. Create Hedge becomes a two-pane workstation: intent and controls on the left, exact proposal and policy evidence on the right.

At mobile widths, navigation becomes an off-canvas drawer. Metrics collapse to two columns; the command and exposure remain above the fold; scenario and ledger rows retain generous tap targets. No horizontal scrolling is allowed.

## Components and States

Small bordered badges carry the persistent truth labels `DEMO`, `REPLAY DATA`, and `SIMULATED EXECUTION`. Buttons are compact rectangles with modest radii; pills are not used as structural containers. Risk checks show both icon and text status. Empty states explain the next safe action. Loading disables the originating action and names the current phase. Errors state the problem in a dismissible red surface.

## Motion

Motion explains state changes through the exposure marker and bounded workflow stages. It respects `prefers-reduced-motion`. Decorative entrance sequences and ambient animation are excluded from this operational surface.

## Identity

The original mark is a flat gold shield containing an eclipsed dark moon. It appears beside the compact HedgeKnight wordmark and uppercase `by Umbra` signature. Binance logos and branded layouts are never copied.
