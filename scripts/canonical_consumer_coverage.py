"""Static field-usage analysis for the in-repository CanonicalStockData consumers."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from typing import Mapping

CANONICAL_CONSUMER_FILES = (
    "main.py",
    "get_sht_report.py",
    "get_med_report.py",
    "get_lng_report.py",
    "get_mak_report.py",
    "get_val_report.py",
    "stock_common/enrich_helpers.py",
    "stock_common/sc_report_runner.py",
)

CANONICAL_CONSUMER_EXEMPTIONS = {
    "bps": "Long report reads BPS from its period-specific financial rows; this Tier 1 field has no report read site.",
    "collected_at": "Local assembly time is audit metadata; report provenance uses upstream effective dates instead.",
    "concepts": "Reports obtain concepts from dedicated concept adapters rather than the canonical quote snapshot.",
    "data_source": "Reports display per-field field_sources; no current report consumes this aggregate source label.",
    "eltdx_seal_amount": "Reports render normalized ELTDX ratios and board state; the raw seal amount has no report read site.",
    "employee_count": "Long report reads employee count from its ZHB company profile payload, not this Tier 1 field.",
    "eps_annual": "Current report helpers render eps and eps_deduct_ttm; annual EPS has no report read site.",
    "fund_5d_array": "Current report helpers render selected daily fund-flow amounts; the five-day array has no report read site.",
    "fund_large_today": "Current report helpers read large-order buy and sell amounts separately, not this aggregate.",
    "fund_main_5d": "Current fund-flow section is daily; the five-day aggregate has no report read site.",
    "fund_main_5d_pct": "Current fund-flow section is daily; the five-day percentage has no report read site.",
    "fund_main_today": "Current fund-flow section reads main buy and sell amounts separately, not this aggregate.",
    "fund_mid_buy": "Current fund-flow section renders main, super-large, and large orders; middle-order buy has no report read site.",
    "fund_mid_sell": "Current fund-flow section renders main, super-large, and large orders; middle-order sell has no report read site.",
    "fund_mid_today": "Current report helpers do not render the middle-order aggregate.",
    "fund_small_today": "Current report helpers do not render the small-order aggregate.",
    "fund_super_today": "Current fund-flow section reads super-large buy and sell amounts separately, not this aggregate.",
    "gross_margin": "Med report calculates gross margin from its period-aligned financial adapter result, not this Tier 1 field.",
    "holder_count": "No current report section renders holder count; the specialized holder adapter remains the report data path.",
    "industry_code": "Reports render the canonical industry label or use a dedicated sector mapping; this code has no read site.",
    "industry_code_push2": "Reports render the canonical industry label; the source-specific push2 code has no read site.",
    "name_core": "Reports use name; this compatibility alias has no report read site.",
    "net_assets": "Current financial sections read period-aligned statements through Tier 2 adapters, not this Tier 1 field.",
    "net_profit_margin": "Med report computes margin from period-aligned profit and revenue to avoid mixing periods.",
    "pcf_ttm": "Valuation scan uses its ranking-row payload; this Tier 1 field has no report read site.",
    "ps_ttm": "Valuation scan uses its ranking-row payload; this Tier 1 field has no report read site.",
    "revenue": "Current financial sections read period-aligned statements through Tier 2 adapters, not this Tier 1 field.",
    "roa": "No current report section renders ROA from the canonical quote object.",
    "total_assets": "Current financial sections read period-aligned statements through Tier 2 adapters, not this Tier 1 field.",
    "trading_periods": "Trading periods are routing metadata; report provenance displays quote_date and time_anchor.",
    "vol_ratio": "Reports calculate volume ratios from their selected daily-bar window; this Tier 1 field has no read site.",
    "volume_hand": "No current report section renders canonical volume_hand; report paths use their selected volume and turnover inputs.",
}


@dataclass
class _Scope:
    path: str
    name: str
    node: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef
    function_aliases: dict[str, str] = field(default_factory=dict)
    params: list[str] = field(default_factory=list)
    assignments: list[tuple[set[str], ast.expr]] = field(default_factory=list)
    loops: list[tuple[set[str], ast.expr]] = field(default_factory=list)
    calls: list[ast.Call] = field(default_factory=list)
    returns: list[ast.expr] = field(default_factory=list)
    canonical_vars: set[str] = field(default_factory=set)
    mapping_vars: set[str] = field(default_factory=set)
    constant_vars: dict[str, set[str]] = field(default_factory=dict)
    returns_canonical: bool = False
    returns_mapping: bool = False


def _target_names(target: ast.expr) -> set[str]:
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        names: set[str] = set()
        for item in target.elts:
            names.update(_target_names(item))
        return names
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    return set()


def _scope_nodes(nodes: list[ast.stmt]):
    stack: list[ast.AST] = list(reversed(nodes))
    while stack:
        node = stack.pop()
        yield node
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            continue
        stack.extend(reversed(list(ast.iter_child_nodes(node))))


def _parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    result = [arg.arg for arg in node.args.posonlyargs + node.args.args]
    if node.args.vararg is not None:
        result.append(node.args.vararg.arg)
    result.extend(arg.arg for arg in node.args.kwonlyargs)
    if node.args.kwarg is not None:
        result.append(node.args.kwarg.arg)
    return result


def _function_name(call: ast.Call) -> str | None:
    if isinstance(call.func, ast.Name):
        return call.func.id
    if isinstance(call.func, ast.Attribute):
        return call.func.attr
    return None


def _resolved_function_name(call: ast.Call, scope: _Scope) -> str | None:
    name = _function_name(call)
    return scope.function_aliases.get(name, name) if name is not None else None


def _imported_getter_names(tree: ast.Module) -> set[str]:
    names = {"get_canonical_stock_data", "get_canonical_stock_data_batch"}
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name in names:
                    names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "core.data_provider":
                    names.add(alias.asname or "core")
    return names


def _contains_getter_reference(node: ast.AST, getter_names: set[str]) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Name) and child.id in getter_names:
            return True
        if isinstance(child, ast.Attribute) and child.attr in {
            "get_canonical_stock_data",
            "get_canonical_stock_data_batch",
        }:
            return True
    return False


def _constant_field_names(
    node: ast.AST,
    field_names: set[str],
    scope: _Scope,
) -> set[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value} if node.value in field_names else set()
    if isinstance(node, ast.Name):
        return scope.constant_vars.get(node.id, set()).copy()
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        result: set[str] = set()
        for item in node.elts:
            result.update(_constant_field_names(item, field_names, scope))
        return result
    return set()


def _is_getter_call(call: ast.Call, getter_names: set[str]) -> bool:
    if isinstance(call.func, ast.Name) and call.func.id in getter_names:
        return True
    if isinstance(call.func, ast.Attribute) and call.func.attr in {
        "get_canonical_stock_data",
        "get_canonical_stock_data_batch",
    }:
        return True
    if isinstance(call.func, ast.Attribute) and call.func.attr in {
        "to_thread",
        "run_in_executor",
    }:
        return any(_contains_getter_reference(arg, getter_names) for arg in call.args)
    return False


def _is_canonical_expr(
    node: ast.AST,
    scope: _Scope,
    getter_names: set[str],
    functions_by_name: dict[str, list[_Scope]],
) -> bool:
    if isinstance(node, ast.Await):
        return _is_canonical_expr(node.value, scope, getter_names, functions_by_name)
    if isinstance(node, ast.Name):
        return node.id in scope.canonical_vars
    if isinstance(node, ast.Call):
        if _is_getter_call(node, getter_names):
            return True
        candidates = functions_by_name.get(_resolved_function_name(node, scope) or "", [])
        return len(candidates) == 1 and candidates[0].returns_canonical
    if isinstance(node, ast.IfExp):
        return _is_canonical_expr(
            node.body, scope, getter_names, functions_by_name
        ) or _is_canonical_expr(node.orelse, scope, getter_names, functions_by_name)
    if isinstance(node, ast.BoolOp):
        return any(
            _is_canonical_expr(value, scope, getter_names, functions_by_name)
            for value in node.values
        )
    return False


def _is_mapping_expr(
    node: ast.AST,
    scope: _Scope,
    getter_names: set[str],
    functions_by_name: dict[str, list[_Scope]],
) -> bool:
    if isinstance(node, ast.Await):
        return _is_mapping_expr(node.value, scope, getter_names, functions_by_name)
    if isinstance(node, ast.Name):
        return node.id in scope.mapping_vars
    if isinstance(node, ast.IfExp):
        return _is_mapping_expr(
            node.body, scope, getter_names, functions_by_name
        ) or _is_mapping_expr(node.orelse, scope, getter_names, functions_by_name)
    if isinstance(node, ast.BoolOp):
        return any(
            _is_mapping_expr(value, scope, getter_names, functions_by_name) for value in node.values
        )
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "to_dict":
            return _is_canonical_expr(node.func.value, scope, getter_names, functions_by_name)
        if isinstance(node.func, ast.Name) and node.func.id == "dict":
            return any(
                _is_mapping_expr(arg, scope, getter_names, functions_by_name) for arg in node.args
            )
        candidates = functions_by_name.get(_resolved_function_name(node, scope) or "", [])
        return len(candidates) == 1 and candidates[0].returns_mapping
    return False


def _callee_arguments(call: ast.Call, target: _Scope) -> list[tuple[str, ast.expr]]:
    params = target.params
    pairs: list[tuple[str, ast.expr]] = []
    for index, arg in enumerate(call.args):
        if index < len(params):
            pairs.append((params[index], arg))
    for keyword in call.keywords:
        if keyword.arg in params:
            pairs.append((keyword.arg, keyword.value))
    return pairs


def find_canonical_consumer_reads(
    source_texts: Mapping[str, str], field_names: set[str]
) -> dict[str, set[str]]:
    """Return field reads keyed by field, following canonical values into helpers.

    The analyzer deliberately limits itself to static in-repository report consumers.
    It follows direct getter results, simple aliases, ``to_dict()`` mappings, and
    arguments passed to uniquely named local/imported helper functions.
    """
    trees = {path: ast.parse(source, filename=path) for path, source in source_texts.items()}
    scopes: list[_Scope] = []
    getter_names_by_path: dict[str, set[str]] = {}
    for path, tree in trees.items():
        getter_names_by_path[path] = _imported_getter_names(tree)
        function_aliases: dict[str, str] = {}
        for import_node in ast.walk(tree):
            if isinstance(import_node, ast.ImportFrom):
                for alias in import_node.names:
                    if alias.asname:
                        function_aliases[alias.asname] = alias.name
        module_scope = _Scope(
            path=path,
            name="<module>",
            node=tree,
            function_aliases=function_aliases,
        )
        scopes.append(module_scope)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scopes.append(
                    _Scope(
                        path=path,
                        name=node.name,
                        node=node,
                        function_aliases=function_aliases,
                        params=_parameters(node),
                    )
                )

    for scope in scopes:
        body = scope.node.body
        for node in _scope_nodes(body):
            if isinstance(node, ast.Assign):
                scope.assignments.append(
                    (set().union(*(_target_names(t) for t in node.targets)), node.value)
                )
            elif isinstance(node, (ast.AnnAssign, ast.NamedExpr)) and node.value is not None:
                scope.assignments.append((_target_names(node.target), node.value))
            elif isinstance(node, ast.For):
                scope.loops.append((_target_names(node.target), node.iter))
            elif isinstance(node, ast.Call):
                scope.calls.append(node)
            elif isinstance(node, ast.Return) and node.value is not None:
                scope.returns.append(node.value)

    functions_by_name: dict[str, list[_Scope]] = {}
    for scope in scopes:
        if scope.name != "<module>":
            functions_by_name.setdefault(scope.name, []).append(scope)

    changed = True
    while changed:
        changed = False
        for scope in scopes:
            getter_names = getter_names_by_path[scope.path]
            for target_names, iterable in scope.loops:
                constant_values = _constant_field_names(iterable, field_names, scope)
                for name in target_names:
                    old_size = len(scope.constant_vars.get(name, set()))
                    scope.constant_vars.setdefault(name, set()).update(constant_values)
                    changed |= len(scope.constant_vars[name]) != old_size
            for target_names, value in scope.assignments:
                constant_values = _constant_field_names(value, field_names, scope)
                for name in target_names:
                    old_size = len(scope.constant_vars.get(name, set()))
                    scope.constant_vars.setdefault(name, set()).update(constant_values)
                    changed |= len(scope.constant_vars[name]) != old_size
                if _is_canonical_expr(value, scope, getter_names, functions_by_name):
                    for name in target_names:
                        if name not in scope.canonical_vars:
                            scope.canonical_vars.add(name)
                            changed = True
                elif _is_mapping_expr(value, scope, getter_names, functions_by_name):
                    for name in target_names:
                        if name not in scope.mapping_vars:
                            scope.mapping_vars.add(name)
                            changed = True
            for value in scope.returns:
                if _is_canonical_expr(value, scope, getter_names, functions_by_name):
                    if not scope.returns_canonical:
                        scope.returns_canonical = True
                        changed = True
                elif _is_mapping_expr(value, scope, getter_names, functions_by_name):
                    if not scope.returns_mapping:
                        scope.returns_mapping = True
                        changed = True
            for call in scope.calls:
                candidates = functions_by_name.get(_resolved_function_name(call, scope) or "", [])
                if len(candidates) != 1:
                    continue
                target_scope = candidates[0]
                for param, arg in _callee_arguments(call, target_scope):
                    constant_values = _constant_field_names(arg, field_names, scope)
                    old_constant_count = len(target_scope.constant_vars.get(param, set()))
                    target_scope.constant_vars.setdefault(param, set()).update(constant_values)
                    changed |= len(target_scope.constant_vars[param]) != old_constant_count
                    if _is_canonical_expr(arg, scope, getter_names, functions_by_name):
                        if param not in target_scope.canonical_vars:
                            target_scope.canonical_vars.add(param)
                            changed = True
                    elif _is_mapping_expr(arg, scope, getter_names, functions_by_name):
                        if param not in target_scope.mapping_vars:
                            target_scope.mapping_vars.add(param)
                            changed = True

    reads: dict[str, set[str]] = {name: set() for name in field_names}
    for scope in scopes:
        getter_names = getter_names_by_path[scope.path]
        for node in _scope_nodes(scope.node.body):
            if isinstance(node, ast.Attribute) and node.attr in field_names:
                if _is_canonical_expr(node.value, scope, getter_names, functions_by_name):
                    reads[node.attr].add(scope.path)
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
                and len(node.args) > 1
            ):
                if _is_canonical_expr(node.args[0], scope, getter_names, functions_by_name):
                    for name in _constant_field_names(node.args[1], field_names, scope):
                        reads[name].add(scope.path)
            elif (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and node.args
            ):
                if _is_mapping_expr(node.func.value, scope, getter_names, functions_by_name):
                    for name in _constant_field_names(node.args[0], field_names, scope):
                        reads[name].add(scope.path)
            elif isinstance(node, ast.Subscript) and _is_mapping_expr(
                node.value, scope, getter_names, functions_by_name
            ):
                for name in _constant_field_names(node.slice, field_names, scope):
                    reads[name].add(scope.path)
    return {name: paths for name, paths in reads.items() if paths}
