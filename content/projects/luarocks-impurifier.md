# luarocks-impurifier

Create native binary rocks from prepared Lua modules and shared libraries.
Original code is MIT; Lua, LuaRocks and payloads retain their own licenses.

```nix
backend.makeRock {
  name = "example-library";
  version = "1.0-1";
  payload = preparedTree;
  sourceUrl = "https://example.org/source";
  luaModules."example.helpers" = "helpers.lua";
  nativeModules."example.native" = "native.so";
  dependencies = [ "lua >= 5.5, < 5.6" ];
  license = "MIT";
}
```

`backend` is `import (inputs.luarocks-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
`version` includes LuaRocks' package revision. Module maps name their logical
Lua module and a relative prepared file. Native files must be .so or .dll;
their basenames are staged to match their declared module names. `summary`,
`dependencies` and `license` become native rockspec metadata. The default license
is unknown. `sourceUrl` is required provenance metadata; packaging uses the
prepared tree and does not fetch or compile that source.

Native `luarocks make` installs the prepared files through its builtin install
backend, then `luarocks pack` emits the binary rock and native manifest. Archive
timestamps are normalized. Build-time dependency downloads are disabled;
consumers retain normal dependency policy. Production source rebuilds, repository
publication and signing are separate concerns.

The SDK uses pkgs.lua and its matching luaPackages.luarocks. Prepared code must
match that Lua ABI and target architecture; express those constraints in native
dependencies. It does not relocate libraries, infer external native dependencies
or require a target Nix daemon/database.

`nix flake check -L` installs, loads, upgrades and removes real binary rocks in a
QEMU VM. A compiled Lua 5.5 extension executes from the native target tree; the
consumer checks dependencies and removal makes require fail. This verifies the
pinned Lua ABI and Linux architecture, not every Lua or LuaJIT configuration.
