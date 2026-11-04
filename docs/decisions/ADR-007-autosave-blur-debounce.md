# ADR-007: Auto-Save on Blur with 500ms Debounce for Long-Form Fields

## Status
Accepted

## Date
2026-11-03

## Context

The frontend needs to persist user input without requiring an explicit "Save" button. The paper planner this app replicates has no save button — you write and it stays. The digital version should feel the same.

Two types of fields exist:
- **Short fields** (time blocks, day summaries, goal fields): single-line or small multi-line text inputs
- **Long-form fields** (Notes, To Do List): large free-text areas where the user may type for extended periods

## Decision

- **All fields:** save on `blur` (when the user tabs away or clicks another element)
- **Long-form text areas** (Notes): additionally debounce-save 500ms after the user stops typing

Both mechanisms call the same `PUT` endpoint. If the network is fast, the blur and debounce saves may overlap; the server handles this safely via upsert semantics.

A subtle "Saved" indicator appears for 2 seconds after each successful save.

```typescript
// Short field: save on blur only
<RuledField
  value={page.study_topic}
  onChange={(e) => update({ study_topic: e.target.value })}
  onBlur={() => save({ study_topic: page.study_topic })}
/>

// Long-form: blur save + 500ms debounce
const debouncedSave = useCallback(
  (patch) => {
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => save(patch), 500);
  },
  [save],
);
```

## Alternatives Considered

### Explicit save button
- Pros: User controls when data is sent; no accidental partial saves
- Cons: Users must remember to save; loses data on accidental tab close; doesn't match paper planner metaphor
- Rejected: The defining UX goal is "write and it stays"

### Save on every keystroke (no debounce)
- Pros: Maximum durability — every character is saved immediately
- Cons: Generates one PUT request per keystroke in long-form fields; 10 WPM = 600 PUT requests per hour; stresses the server and creates noisy audit logs
- Rejected: Debouncing at 500ms achieves durability without request noise

### Periodic timer save (autosave every N seconds)
- Pros: Simple implementation, predictable save frequency
- Cons: User may type for 4.9 seconds, switch tabs, and lose work; or may be idle and send empty saves
- Rejected: Blur-triggered save is more reliable — it fires exactly when the user is "done" with a field

### Save on navigation (before leaving the page)
- Pros: Catches any unsaved state at page transition
- Cons: `beforeunload` events are unreliable in modern browsers; hard to make async; duplicates the blur behavior
- Rejected: Blur-on-tab-switch already covers this for in-app navigation; `beforeunload` is unnecessary if blur is reliable

## Consequences

- **Positive:** Data is saved the moment the user moves to the next field — indistinguishable from paper.
- **Positive:** Long-form fields are saved while typing, preventing loss if the user closes the tab mid-paragraph.
- **Negative:** A save request fires on every blur even if the field hasn't changed. This is acceptable — the PUT is an upsert with identical data; no corruption results.
- **Negative:** If the user types in the Notes field and immediately closes the browser tab within 500ms, the last keystrokes may be lost. This is an acceptable edge case for a planner app.
