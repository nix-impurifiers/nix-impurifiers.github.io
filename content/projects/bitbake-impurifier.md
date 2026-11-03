# BitBake impurifier

Generate an OpenEmbedded layer for Nix application closures. BitBake is the
execution engine; OpenEmbedded supplies the recipes, packaging classes and
image construction. Yocto distributions consume this layer.

Original adapter code is MIT. The pinned BitBake and Pseudo SDKs retain their
upstream licenses and notices.

```nix
let
  adapter = inputs.bitbake-impurifier.lib.bitbake-impurifier { inherit pkgs; };
in adapter.makeLayer {
  applications = [ (adapter.makeOfflineRecipe { pkg = pkgs.hello; }) ];
  runtime = adapter.makeRuntime {
    nixDependency = "my-nix-provider";
    pythonDependency = "python3-core";
  };
}
```

Add the resulting `meta-nix-impurifier` directory to `BBLAYERS`, then add the
application recipe names to your image. Runtime dependencies name your real
Nix and Python providers. Building or installing Nix itself is deferred.

`makeNetRecipe` and `makeOfflineRecipe` accept the shared payload options,
including configuration files, native service intent and host-library capture.
`hostDependencies` adds OpenEmbedded runtime dependency expressions. Set
`license` and `licenseFile` to the actual application license and its source text;
the emitter records and verifies that file through native OE licensing tasks.
`makeLayer` combines applications and the runtime and accepts
`compatibleSeries` (default `wrynose`, the tested OE release series).

The package class preserves prebuilt payload bytes: it does not strip ELF
files, split debug data or infer target dependencies from opaque Nix cache
contents. Nix tracks that closure; native dependencies describe the host.
Application recipe licensing defaults to OE's `CLOSED` marker until callers
supply `license` and `licenseFile`, avoiding invented metadata for arbitrary
closures. This does not
relicense their contents; the runtime recipe and original code are MIT.

Activation uses native `pkg_postinst_ontarget`: image construction queues it
through OpenEmbedded's real first-boot intercept instead of executing against
the build host. Target transactions reconcile the shared profile. Offline
removal skips target activation. Keep the normal first-boot postinstall runner
in your image and provide writable Nix state.

Native SDK and VM test coverage is developed against BitBake 2.18.0 and
OpenEmbedded Core Yocto 6.0.4. Full machine image/boot coverage and other
architectures must be distinguished from recipe and native package tests.
