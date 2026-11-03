# pip-impurifier

Build wheels from producer-prepared Python distributions, including native libraries.
Original code is MIT. Upstream Python and pip retain their licenses.

```nix
backend.makeWheel { name = "my-package"; version = "1.0"; payload = preparedTree; }
```

`payload` is the wheel's import tree. `tag` defaults to `py3-none-any`; set a
platform/ABI tag and `pure = false` for native files. `dependencies` carries
native Python requirements; `entryPoints` maps console script names to
`module:function`. `summary` supplies metadata. Tags describe compatibility,
not relocation: producers supply files that already work for the consumer ABI.
Symlinks must be materialized. Metadata and hashed RECORD entries are generated
reproducibly. No Nix client, database, daemon or install hooks are added.

Install with `pip install ./result/*.whl`, uv or another compatible installer.
The QEMU suite uses real pip and a venv to install, import a compiled native
library, upgrade, check dependencies and uninstall. Python/pip are NixOS fixture
tools; this does not claim a full Nix-free operating-system boot. Registry
publication and further platform/ABI tags require their own validation.
