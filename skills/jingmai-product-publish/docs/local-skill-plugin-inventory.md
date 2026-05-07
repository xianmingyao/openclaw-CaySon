# Local Skill and Plugin Inventory

Updated: 2026-05-07

## Discovery Roots

- `C:\Users\Administrator\.codex\plugins`
- `C:\Users\Administrator\.codex\skills`
- `C:\Users\Administrator\.agents\skills`

## Current Model

- Plugins are registered through `C:\Users\Administrator\.codex\config.toml` marketplace entries.
- Skills under `C:\Users\Administrator\.codex\skills` and `C:\Users\Administrator\.agents\skills` are discovered natively and do not require custom `skills` entries in `config.toml`.

## Registered Local Plugin Marketplaces

- `openai-bundled`
  - Source: `c:\users\administrator\.codex\.tmp\bundled-marketplaces\openai-bundled`
- `openai-primary-runtime`
  - Source: `c:\users\administrator\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime`
- `superpowers-local`
  - Source: `c:\users\administrator\.agents\plugins\superpowers-marketplace`
- `claude-mem-local`
  - Source: `c:\users\administrator\.codex\plugins\claude-mem\.agents\plugins`

## Local Inventory Summary

- `C:\Users\Administrator\.codex\skills`: 94 directories
- `C:\Users\Administrator\.agents\skills`: 167 directories
- `C:\Users\Administrator\.codex\plugins` local plugin repos: 2
  - `claude-mem`
  - `superpowers`

## Notes

- `superpowers` is already available in both forms:
  - marketplace plugin via `superpowers-local`
  - native skill package under `C:\Users\Administrator\.agents\skills\superpowers`
- `claude-mem` native skills already exist under `C:\Users\Administrator\.agents\skills\claude-mem`
- No additional custom skill-root settings were added to `config.toml` because local install docs indicate native skill discovery should use the filesystem directly.
