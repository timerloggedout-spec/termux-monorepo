"""CLI — one consumer of the labbook/1 contract (row 11).

    python -m labbook [--project DIR] compile <pipeline-module:attr>
    python -m labbook [--project DIR] run <ir.yml> [--param k=v]...
    python -m labbook [--project DIR] catalog list
    python -m labbook [--project DIR] show-run <run_id>
    python -m labbook [--project DIR] latest <asset>
    python -m labbook [--project DIR] compare <run_a> <run_b>
    python -m labbook [--project DIR] promote <asset> <alias> <materialization_id>
    python -m labbook [--project DIR] verify <run_id>
    python -m labbook verify-bundle <bundle.zip>
    python -m labbook [--project DIR] export <run_id> <bundle.zip>

Exit code is 0 only when the operation's verdict is a pass; a run whose
verdict enumerates a failed node exits 1 *with the enumeration printed*
— never a bare failure, never a bare success (row 6).
"""

import argparse
import importlib
import json
import sys

from . import compiler
from .api import Labbook, open_project


def _print(obj):
    print(json.dumps(obj, indent=1, sort_keys=True, default=str))


def _params(pairs):
    out = {}
    for p in pairs or []:
        k, _, v = p.partition("=")
        for conv in (int, float):
            try:
                v = conv(v)
                break
            except ValueError:
                continue
        out[k] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog="labbook")
    ap.add_argument("--project", default=".")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("compile")
    p.add_argument("pipeline", help="module:attr naming a Pipeline")
    p.add_argument("-o", "--out")

    p = sub.add_parser("run")
    p.add_argument("ir")
    p.add_argument("--param", action="append")
    p.add_argument("--actor")

    p = sub.add_parser("catalog")
    p.add_argument("action", choices=["list"])

    p = sub.add_parser("show-run")
    p.add_argument("run_id")

    p = sub.add_parser("latest")
    p.add_argument("asset")

    p = sub.add_parser("compare")
    p.add_argument("run_a")
    p.add_argument("run_b")

    p = sub.add_parser("promote")
    p.add_argument("asset")
    p.add_argument("alias")
    p.add_argument("materialization_id")
    p.add_argument("--actor")

    p = sub.add_parser("verify")
    p.add_argument("run_id")

    p = sub.add_parser("verify-bundle")
    p.add_argument("bundle")

    p = sub.add_parser("export")
    p.add_argument("run_id")
    p.add_argument("out")

    args = ap.parse_args(argv)

    if args.cmd == "verify-bundle":
        result = Labbook.verify_bundle(args.bundle)
        _print(result)
        return 0 if result["pass"] else 1

    lb = open_project(args.project)
    try:
        if args.cmd == "compile":
            module_name, attr = args.pipeline.split(":")
            pipeline = getattr(importlib.import_module(module_name), attr)
            ir = lb.compile(pipeline)
            text = compiler.ir_to_yaml(ir)
            if args.out:
                with open(args.out, "w") as f:
                    f.write(text)
            else:
                print(text)
            return 0
        if args.cmd == "run":
            with open(args.ir) as f:
                ir = compiler.ir_from_yaml(f.read())
            verdict = lb.run(ir, params=_params(args.param), actor=args.actor)
            _print(verdict)
            return 0 if verdict["ok"] else 1
        if args.cmd == "catalog":
            _print(lb.catalog_list())
            return 0
        if args.cmd == "show-run":
            _print(lb.get_run(args.run_id))
            return 0
        if args.cmd == "latest":
            _print(lb.latest(args.asset))
            return 0
        if args.cmd == "compare":
            _print(lb.compare(args.run_a, args.run_b))
            return 0
        if args.cmd == "promote":
            _print(lb.promote(args.asset, args.alias,
                              args.materialization_id, actor=args.actor))
            return 0
        if args.cmd == "verify":
            result = lb.verify(args.run_id)
            _print(result)
            return 0 if result["pass"] else 1
        if args.cmd == "export":
            print(lb.export_bundle(args.run_id, args.out))
            return 0
    finally:
        lb.close()
    return 2


if __name__ == "__main__":
    sys.exit(main())
