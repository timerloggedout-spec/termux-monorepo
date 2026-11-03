"""Gate conditions (ledger row 6).

Gates are condition *data* in the IR — an expression over named outputs
(metric values and params), evaluated by a whitelisted AST walker. No
eval(), no arbitrary code: a gate the evaluator cannot interpret is a
hard error naming the construct, never a silent pass or skip.
"""

import ast
import operator

from .errors import LabbookError

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_CMPS = {
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
}


def evaluate(expression: str, names: dict):
    """Evaluate a gate expression. Returns (result, inputs_used) where
    inputs_used records every name's value at evaluation time — the run
    record carries both for any skip (row 6)."""
    used = {}

    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, str, bool)) or node.value is None:
                return node.value
            raise LabbookError("gate constant of unsupported type",
                               value=repr(node.value))
        if isinstance(node, ast.Name):
            if node.id not in names:
                raise LabbookError(
                    "gate references an unknown name",
                    value=node.id,
                    expected=f"one of {sorted(names)} (metrics logged by "
                    "upstream nodes, or declared params)",
                    fix="log the metric upstream or fix the gate expression",
                )
            used[node.id] = names[node.id]
            return names[node.id]
        if isinstance(node, ast.BoolOp):
            vals = [ev(v) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(vals)
            if isinstance(node.op, ast.Or):
                return any(vals)
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return not ev(node.operand)
            if isinstance(node.op, ast.USub):
                return -ev(node.operand)
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.Compare):
            left = ev(node.left)
            for op, comp in zip(node.ops, node.comparators):
                if type(op) not in _CMPS:
                    raise LabbookError("gate comparison is not supported",
                                       value=ast.dump(op))
                right = ev(comp)
                if not _CMPS[type(op)](left, right):
                    return False
                left = right
            return True
        raise LabbookError(
            "gate expression uses an unsupported construct",
            value=ast.dump(node),
            expected="names, numbers, strings, comparisons, and/or/not, "
            "+ - * / — gates are data, not code",
        )

    tree = ast.parse(expression, mode="eval")
    return ev(tree), used
