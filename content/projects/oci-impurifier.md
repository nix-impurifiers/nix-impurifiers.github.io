# oci-impurifier

Build ordinary OCI image layouts for container runtimes. This is distinct from
bootc's bootable OS image contract. Original code is MIT; payloads retain their
own licenses.

`makeImage { pkg; program ? pkg.meta.mainProgram; }` embeds a complete Nix-built
application closure at its original store paths and chooses its entrypoint.
There is no target Nix database, daemon, client or profile activation. The
container manager owns the entire image filesystem and its retention.

`makeNativeImage { rootfs; }` accepts a complete prepared filesystem tree, without
adding a store. Both constructors accept `name`, `tag`, `architecture` and OCI
`config`; the native constructor also accepts `os`. Set metadata for the actual
target ABI; the emitter does not cross-compile or relocate files. Creation time,
file ownership, tar ordering and JSON are normalized for reproducibility.

Use skopeo to copy `oci:result:latest` into a native runtime or registry. The VM
uses real skopeo and Podman to load and execute native and closure images without
networking, replace a tag with a new application version, and remove images.
It also unpacks the native image and checks it has no `/nix` tree. Registry
credentials, signing and publication are consumer workflows, not build inputs.
