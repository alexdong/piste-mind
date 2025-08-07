.PHONY: dev test run web serve

dev:
	uv run ruff check . --fix --unsafe-fixes
	uv run ruff format .
	uv run ty check .

test:
	uv run pytest --lf

run:
	uv run python -m piste_mind.cli --model sonnet

web:
	uv run python -m piste_mind.web

serve:
	./tools/run_with_tunnel.sh
