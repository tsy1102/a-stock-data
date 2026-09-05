#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analyze sc_datasource.py structure to inform a safe split (read-only)."""
import ast, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "stock_common", "sc_datasource.py")
src = open(SRC, encoding="utf-8").read()
tree = ast.parse(src)

defs = []          # (name, lineno, end_lineno, is_class)
other = []         # non-def top-level nodes
for n in tree.body:
    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
        defs.append((n.name, n.lineno, getattr(n, "end_lineno", n.lineno), False))
    elif isinstance(n, ast.ClassDef):
        defs.append((n.name, n.lineno, getattr(n, "end_lineno", n.lineno), True))
    else:
        other.append(n)

print(f"TOTAL top-level defs/classes: {len(defs)}")
print(f"  functions: {sum(1 for d in defs if not d[3])}")
print(f"  classes:   {sum(1 for d in defs if d[3])}")
print(f"TOTAL non-def top-level nodes: {len(other)}")
for n in other:
    kind = type(n).__name__
    extra = ""
    if isinstance(n, (ast.Import, ast.ImportFrom)):
        mod = getattr(n, "module", None)
        names = [a.name for a in n.names]
        extra = f"  {mod or ''} <- {names}"
    elif isinstance(n, (ast.Assign, ast.AnnAssign)):
        extra = "  " + ast.unparse(n).splitlines()[0][:80]
    print(f"  [{kind}]{extra}")

# self-imports?
print("\n=== self-import scan (from stock_common.sc_datasource / from . import) ===")
for n in tree.body:
    if isinstance(n, ast.ImportFrom):
        if n.module and ("sc_datasource" in n.module):
            print(f"  line {n.lineno}: from {n.module} import {[a.name for a in n.names]}")
        if n.level and n.module is None:
            print(f"  line {n.lineno}: relative import {[a.name for a in n.names]}")

# __all__ / __name__ guard
print("\n=== __all__ / __main__ guard ===")
for n in other:
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name) and t.id == "__all__":
                print(f"  __all__ at line {n.lineno}")
    if isinstance(n, ast.If):
        test = ast.unparse(n.test)
        if "__name__" in test:
            print(f"  __name__ guard at line {n.lineno}: {test}")

# class bodies with calls at class scope (exec-time risk)
print("\n=== classes with class-body Call (exec-time risk) ===")
for n in tree.body:
    if isinstance(n, ast.ClassDef):
        for stmt in n.body:
            if isinstance(stmt, ast.Assign):
                for v in ast.walk(stmt.value):
                    if isinstance(v, ast.Call):
                        print(f"  class {n.name} line {n.lineno}: class-level call {ast.unparse(stmt.value)[:60]}")
                        break

# module-level calls (non-def nodes that call functions) - risk for ordering
print("\n=== module-level executable calls (non-def, non-import) ===")
for n in other:
    if isinstance(n, (ast.Assign, ast.Expr, ast.AugAssign, ast.AnnAssign)):
        for v in ast.walk(n):
            if isinstance(v, ast.Call) and isinstance(v.func, ast.Name):
                print(f"  line {n.lineno}: {ast.unparse(n).splitlines()[0][:70]}")
                break
