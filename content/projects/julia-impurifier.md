# julia-impurifier

Export prepared trees as Julia Pkg artifacts with native identity and downloads.
Original code is MIT; Julia and payloads retain their own licenses.

```nix
backend.makeArtifact {
  name = "example";
  payload = preparedTree;
  downloadUrl = "https://example.org/artifact.tar.gz";
  platform = { arch = "x86_64"; os = "linux"; libc = "glibc"; };
}
```

`backend` is `import (inputs.julia-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
The output contains artifact.tar.gz, Artifacts.toml and git-tree-sha1. Native
Pkg.Artifacts computes the Git-tree identity and binds the named artifact to its
SHA-256-checked download. Archive metadata is normalized without changing tree
identity. `platform` is optional for platform-independent data; otherwise supply
arch/os and suitable native platform tags. `lazy` defaults to false. HTTP and file URLs are also accepted; transport and binding distribution
policy belong to the producer. Native download checksums remain enforced.

Publish the archive at downloadUrl and distribute the binding with a Julia
package or application. Consumers use Pkg.Artifacts normally. This backend
produces artifacts, not a registry, project environment manager or new Julia
package-build system. Julia code can locate the artifact and load its libraries
or data. Prepared files must already match their declared ABI; libc is not
assumed when platform is omitted. No Nix daemon, database or client is added,
and no relocation is attempted. External library dependencies remain the
producer's responsibility.

`nix flake check -L` downloads two native artifacts from a VM-local HTTP feed
using actual Julia, verifies their identities and executes a compiled shared
library from the artifact depot. It removes the second artifact, rejects a
corrupted download, recovers with the correct archive, removes it again and
requires failure when the feed is offline. The pinned Linux Julia/runtime and
native platform binding are tested; further platform tags need their own tests. A native binding check also covers
platform-independent data without OS/libc tags.
