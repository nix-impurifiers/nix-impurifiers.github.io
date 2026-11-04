# systemd-portable-impurifier

Build native portable-service images containing Nix-built closures. Original
code is MIT; systemd and payloads retain their own licenses.

```nix
backend.makeImage {
  pkg = application;
  name = "example";
  version = "1";
  units."example.service" = ''
    [Service]
    ExecStart=${application}/bin/example
  '';
}
```

`backend` is `import (inputs.systemd-portable-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
`makeImage { pkg; name; version; units; osRelease ? ...; }` creates a SquashFS
image named `name_version.raw`. It embeds the complete pkg closure at its original
store paths, native units and os-release. Unit filenames must use the image-name
prefix. Unit executables and helpers must belong to the supplied closure.
`makeNativeImage { rootfs; name; version; }` accepts an entirely prepared native
root filesystem instead, including its own units, runtime and mount placeholders.

Attach with native `portablectl attach`, choose an appropriate native profile,
and start the attached unit. Stop and detach before replacing an image. The
image is read-only; use native systemd state/cache/runtime directory settings
for services needing writable state. The backend does not start services, select a host trust profile, manage a system or
add target Nix intent. No Nix daemon, database or client is required. Payloads
must already match the target kernel/ABI; nothing is relocated. Image signing
and host image-verification policy remain consumer operations.

`nix flake check -L` attaches the actual raw image in a QEMU VM, runs a service
inside its RootImage, verifies no target Nix database/socket, stops/detaches,
attaches a second revision and runs it, then detaches and proves the unit is gone.
The fixture explicitly chooses systemd's trusted profile for this unsigned local
image. Other sandbox profiles, signatures and host policies need separate tests.
