"""deepcli.llm — provider adapter layer.

Mev (observatory producer) and Jev (observatory judge) route every call
through ``deepcli.llm.adapters.<provider>``; each adapter module exposes an
``Adapter`` class with an async ``ask(prompt)`` returning a Response-shaped
object (text / tokens_in / tokens_out / cost_usd). Adapters are stdlib-only
and read their credentials from the environment — never from arguments,
files, or the repository.
"""
