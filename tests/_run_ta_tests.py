import sys, types, importlib.util, traceback

# 桩：让测试文件的 `import pytest` 可用（本环境未装 pytest）
sys.modules['pytest'] = types.ModuleType('pytest')

ROOT = r'C:/Tencent/WorkBuddy/a-stock-data'
sys.path.insert(0, ROOT)

spec = importlib.util.spec_from_file_location(
    'ta_tests', ROOT + r'/tests/test_sc_ta_core.py'
)
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
except Exception as e:
    print('MODULE IMPORT FAILED:', repr(e))
    traceback.print_exc()
    sys.exit(2)

passed = failed = 0
for n in dir(mod):
    if n.startswith('test_') and callable(getattr(mod, n)):
        try:
            getattr(mod, n)()
            print('PASS', n)
            passed += 1
        except Exception as e:
            print('FAIL', n, '->', repr(e))
            failed += 1

print(f'\n==> {passed} passed, {failed} failed')
sys.exit(1 if failed else 0)
