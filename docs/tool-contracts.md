# Blue Whale — Tool Contracts

## check_decision_drift

Owner: Ana Balukhashvili (@anaBalukha)

**Model-facing description:** Compare supplied previous project
decisions with proposed decisions and report conflicts. Read-only.

| Property | Contract |
|---|---|
| Effect | Reads and compares supplied data |
| Undo | Nothing to undo |
| Idempotent | Yes |
| Offered to | Visitors and signed-in users |
| Identity | Not needed; never a tool argument |
| Touches | src/drift_core.py in memory; no database writes |
| Must never | Change confirmed decisions, fabricate user approval, access arbitrary paths, or accept model-supplied user_changes |

### Inputs

- `state`: 1–8 prior decisions, supplied as a JSON object.
- `candidate`: 1–8 proposed decisions, supplied as a JSON object.
- Keys: lowercase ASCII letters, numbers and underscores;
  start with a letter; maximum 32 characters.
- Values: 1–80 characters, starting with an ASCII letter or digit;
  remaining characters limited to letters, digits, spaces,
  underscores and selected ordinary punctuation.
- Extra arguments are forbidden.
- No identity or user_changes argument is accepted.

The model sees both input fields. The tool compares their contents;
it does not independently authenticate the supplied prior state.
A production caller must obtain trusted state from application-owned
storage rather than treating model text as authoritative.

### Result

- `status`: `drift` or `consistent`
- `effective_state`: dictionary of compared prior decisions
- `conflicts`: list of objects containing `field`, `expected`,
  and `proposed`

### Expected failures

| Failure | Model-facing behavior |
|---|---|
| Missing state or candidate | Explain that the required input is missing |
| Invalid field or value | Refuse with a validation error |
| Forged user_changes | Refuse unexpected argument |
| Unknown tool | Refuse without execution |
| Unexpected execution failure | Return a generic safe error |
| Audit logging unavailable | Return a safe failure |

The shared execution gate validates inputs before running the tool
and logs calls without raw decisions or caller identity.

### Tests

- tests/test_ana_drift_tool.py
- tests/test_ana_mcp.py
- tests/test_tool_golden.py
- evals/tools/anaBalukha.yaml

## HW2 ownership

| Member | HW2 tool |
|---|---|
| Ana Balukhashvili | check_decision_drift |
| Mikheili Kakhniashvili | search_trusted_sources |
| Aleksandre Giorgashvili | Pending confirmation by Aleksandre |

The outstanding owner assignment must be confirmed, not invented.
