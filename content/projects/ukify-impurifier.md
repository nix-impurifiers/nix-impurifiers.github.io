# ukify-impurifier

Compose Nix-built kernels and initramfs artifacts into native UKIs with upstream
ukify. Original code is MIT; systemd, Linux and payloads retain their licenses.

`makeUKI { kernel; initrds = [ initramfs ]; }` produces an **unsigned** EFI file.
It also accepts `cmdline`, `osRelease`, `uname` and `stub`. The default stub is
x86_64; producers targeting another architecture must supply the matching stub
and kernel. Native dracut, mkinitcpio or other builder outputs can be initrds.
No target Nix runtime or relocation is added.

Sign after building, outside Nix and its store:

```
ukify-impurifier sign result --key private.key --certificate certificate.pem --output signed.efi
```

The helper uses native sbsign, verifies the resulting signature with sbverify,
and atomically replaces the output. Private keys are deliberately absent from
the build API. Secure Boot enrollment, disk installation and TPM PCR policies
remain consumer-controlled operations.

The QEMU check enrolls an ephemeral test certificate in Secure-Boot-capable OVMF,
boots initial and updated signed UKIs, checks the guest's actual SecureBoot EFI
variable, and requires firmware rejection after altering the embedded kernel.
The early userspace has no root disk, host store or target Nix database.
