# jingmai-product-publish CLI Reference

ASCII-only command summary for external scripts and automation.

## Environment

```bash
cd E:\workspace\skills\jingmai-product-publish
uv pip install -r requirements.txt
uv run python cli.py --help
python cli.py --help
```

## Status

```bash
uv run python cli.py status
python cli.py status
python cli.py status <task_id>
```

## Publish

```bash
uv run python cli.py publish --config product.json
uv run python cli.py publish --data "{\"title\":\"Test Product\",\"price\":29.9}"
uv run python cli.py publish --config product.json --plan-out data\last-plan.json

python cli.py publish --config product.json
```

## Plan

```bash
uv run python cli.py plan "Publish a phone case" --config product.json
uv run python cli.py plan --config product.json
uv run python cli.py plan --config product.json --steps-only

python cli.py plan --config product.json
```

## Execute

```bash
uv run python cli.py execute --config plan.json
uv run python cli.py execute --config plan.json --task-id abc123
uv run python cli.py execute --config plan.json --from-start

python cli.py execute --config plan.json
```

Notes:

- Default behavior resumes from the first non-`success` step.
- `--from-start` forces a full rerun from step 1.

## Batch

```bash
uv run python cli.py batch --file products.xlsx
uv run python cli.py batch --file products.json
uv run python cli.py batch --dir .\products
uv run python cli.py batch --file products.json --stop-on-error
uv run python cli.py batch --file products.json --plan-out data\plans

python cli.py batch --file products.json
```

## Scrape

```bash
uv run python cli.py scrape https://item.jd.com/12345678.html
uv run python cli.py scrape --url https://item.jd.com/12345678.html --output product.json
uv run python cli.py scrape https://item.jd.com/12345678.html --no-save

python cli.py scrape --url https://item.jd.com/12345678.html
```

## Think

```bash
uv run python cli.py think --question "Why did the current page fail?"
uv run python cli.py think --screenshot resources\screenshots\shot.png
uv run python cli.py think "What is wrong with the current page?"

python cli.py think --question "Check this page state"
```

## Actions

```bash
uv run python cli.py actions
python cli.py actions
```

## Tasks

```bash
uv run python cli.py tasks
uv run python cli.py tasks --status running --limit 10

python cli.py tasks --status failed
```

## Products

```bash
uv run python cli.py products --list
uv run python cli.py products --file product.json

python cli.py products --list
```

## Database Init

```bash
uv run python cli.py init-db
uv run python cli.py db init

python cli.py init-db
```

## Memory

```bash
uv run python cli.py memory stats
uv run python cli.py memory search --query "category select" --top 5
uv run python cli.py memory cleanup
uv run python cli.py memory create --content "price readback failed" --type short_term --importance 0.8
uv run python cli.py memory clear --confirm

python cli.py memory stats
```

## Runtime Notes

- `fill_product_info` uses UIA-first readback verification.
- Price fields use normalized numeric comparison.
- Screenshot capture uses real PNG output.
- `JINGMAI_DEBUG_SCREENSHOTS=1` enables extra full-size debug screenshots.
- `execute` supports resume and full rerun semantics.
