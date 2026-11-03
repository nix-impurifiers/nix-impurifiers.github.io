# termux-impurifier

Produce native Termux DEBs from Nix-built **Android-compatible** payloads. This
is distinct from Android application APK packaging and from Debian's runtime ABI.
The installed files need no Nix daemon, executable, database or root-owned store.

```nix
let termux = termux-impurifier.lib.termux-impurifier { inherit pkgs; };
in termux.makeNativePackage {
  name = "my-command";
  version = "1.0";
  architecture = "aarch64";
  payload = myAndroidPrefixTree;
  dependencies = [ "libexample (>= 1)" ];
}
```

The payload is a tree relative to Termux's prefix, such as `bin/my-command` and
`lib/libexample.so`. The DEB places it under `/data/data/com.termux/files/usr` and
includes native installed-file checksums. Staging restores owner-write permission
from Nix’s read-only output modes so native installation works under the app UID. `applicationId` can select a different
Termux app ID; the producer must build for that exact prefix. No relocation is
performed. Supported native architecture names are `aarch64`, `arm`, `i686`,
`x86_64` and `all`; select the ABI actually used by the payload. `all` is for
architecture-independent files. Dependencies are ordinary native package
expressions, optionally with a version comparison.

Install with Termux's native package tools. Keep upstream repo dependencies
compatible with the chosen Termux variant. This adapter does not install the
Termux Android app or manufacture an Android ABI from ordinary Linux outputs.
Bundled Nix is not currently offered here: normal app sandboxes cannot provision
or own a global `/nix` directory. A separate explicitly accessible store would
need its own tested ownership and trust contract.

The VM fixture installs the actual pinned Termux Android app and its embedded
bootstrap. Native package operations run as the app UID, using Termux's own dpkg,
not a host Linux executable. Coverage includes dependencies, installation,
upgrade, checksum diagnostics, refusal to remove a required dependency, removal
and cleanup. The initial device fixture is Android-x86 API 28; other Android
versions and CPU architectures require additional native tests.

Original code is MIT. Upstream application and package licenses remain intact.
