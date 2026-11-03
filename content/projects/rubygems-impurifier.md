# rubygems-impurifier

Build native gems from complete prepared Ruby import trees with real RubyGems.
Original code is MIT; Ruby, RubyGems and payloads retain their own licenses.

`makeGem { name; version; payload; }` accepts `platform`, `requirePaths`,
`executables`, `dependencies`, `summary` and `licenses`. `dependencies` maps gem
names to RubyGems requirement strings. The default platform is `ruby`; native
extensions require an accurate platform and a compatible Ruby ABI. Files should
already work in the installed gem prefix. No Nix runtime, automatic relocation,
install-time compilation, or registry publication is added.

The QEMU suite installs and loads a compiled native Ruby extension with actual
RubyGems, changes versions, verifies the package and uninstalls all versions.
Ruby is a NixOS fixture interpreter; this does not claim a full Nix-free host
boot or compatibility with other Ruby/OS ABIs.

`requiredRubyVersion` declares the consumer Ruby constraint (default `>= 0`);
producers of native extensions should constrain it to the ABI they built for.
