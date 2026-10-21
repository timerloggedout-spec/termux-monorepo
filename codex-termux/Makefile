.PHONY: init doctor build reconcile run

PYTHON ?= python3
BRIDGE_DIR := $(CURDIR)/bridge

init:
	git -C .. submodule update --init --depth 1 codex-termux/codex-termux_fork

doctor:
	PYTHONPATH="$(BRIDGE_DIR)" $(PYTHON) -m codex_bridge doctor

build:
	PYTHONPATH="$(BRIDGE_DIR)" $(PYTHON) -m codex_bridge build

reconcile:
	PYTHONPATH="$(BRIDGE_DIR)" $(PYTHON) -m codex_bridge reconcile

run:
	PYTHONPATH="$(BRIDGE_DIR)" $(PYTHON) -m codex_bridge run $(ARGS)
