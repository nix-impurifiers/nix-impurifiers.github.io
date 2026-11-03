# apptainer-impurifier

Produce native SIF filesystem partitions with upstream Apptainer's SIF tools.
Original code is MIT; Apptainer and payloads retain their licenses.

`makeImage { pkg; program ? pkg.meta.mainProgram; }` embeds a complete Nix-built
closure and a native runscript. `makeNativeImage { rootfs; }` instead accepts a
complete prepared filesystem tree. Both accept `name` and the native numeric
SIF `architecture` code (default 2, amd64). Raw trees supply their own runscript,
shell and runtime files. Payloads must already match the target ABI; no relocation
or target Nix daemon/database is added.

The builder uses mksquashfs and real `apptainer sif new/add`, avoiding privileged
container build steps. SIF IDs/timestamps follow upstream tooling; bit-for-bit
reproducibility of the SIF wrapper is not currently promised. Image signing and
private keys remain external consumer operations.

The QEMU suite runs actual Apptainer as an ordinary user, executes two image
versions under containment, checks that Nix's database/socket are absent, replaces
the image and verifies removal. The NixOS fixture provides the runtime; further
HPC site policy, GPU and architecture combinations need separate coverage.
