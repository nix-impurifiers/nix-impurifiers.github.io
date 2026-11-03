# mkinitcpio-impurifier

Expose Nix-built software through native mkinitcpio build and runtime hooks.
The generated hook embeds complete runtime closures at their original store
paths. The consumer and early userspace need no Nix executable, daemon, or
SQLite database. Original adapter code is MIT.

```nix
let adapter = inputs.mkinitcpio-impurifier.lib.mkinitcpio-impurifier { inherit pkgs; };
in adapter.makeHook {
  pkg = myEarlyBootTool;
  name = "my_tool";
  runtimeHook = myRuntimeHook;
}
```

Install the output's `/usr` tree through your normal packaging tools. Add
`my_tool` to `HOOKS` in the target's mkinitcpio configuration and regenerate its
initramfs normally. `runtimeHook` is optional; without it the hook only includes
the software. Runtime scripts define native functions such as `run_earlyhook`
or `run_hook`, rather than executing a main program at source time. Reference
supplied executables by their original absolute Nix output paths. The runtime
script's own closure is included. The native `add_runscript` function registers
its stages. Inputs need to match the target environment but need not use nixpkgs.

Payload files are staged privately under `/usr/lib/initcpio/impurifiers/<name>`.
The build hook uses mkinitcpio's file/tree helpers without ELF dependency
rediscovery. Native mkinitcpio owns image generation and hook ordering. No Nix
registration, GC, kernel management, signing or system installation is implied.

`native-client` builds upstream mkinitcpio 42.2. Its SDK uses real BusyBox and
native tools from explicit Nix paths, preserves the supplied tool PATH, disables
systemd installation integration, and installs its configuration below its own
prefix. Native mkinitcpio build/runtime logic remains upstream. Original upstream
GPL notices are preserved separately from the adapter's MIT license.

The QEMU test uses the real mkinitcpio builder and init program. A native early
hook executes the supplied tool before root is available, checks absence of a
Nix database, emits a proof and powers off. The guest has no root disk or shared
host store. This is early-userspace coverage, not a complete Arch installation,
Secure Boot, or real hardware qualification.

Run `nix flake check -L`; software QEMU emulation requires no KVM.
