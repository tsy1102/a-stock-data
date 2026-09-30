# Vendored runtime wheel

`easy_tdx-1.20.8-py3-none-any.whl` is built from the upstream
[`yanwei99521/easy-tdx`](https://github.com/yanwei99521/easy-tdx) commit
`41e56376fafa3abae0f6538f271eafd6af26d27f`.

The pinned upstream `pyproject.toml` force-includes `web-ui/dist`, which is not
present in that commit. The wheel was built after removing only that
`force-include` entry; the wheel's `packages = ["src/easy_tdx"]` setting and all
Python package files are unchanged. The project does not use the optional web UI
distribution. `requirements.txt` installs this local wheel so a fresh checkout
can install dependencies directly without rebuilding the broken upstream Git
source.

SHA-256:

```text
8bec61e2d8fa55801e8c22dad2a6f8c3ef91e9ce97ef5c395ebe299bcd40163f
```
