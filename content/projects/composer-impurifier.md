# composer-impurifier

Package prepared PHP trees as native Composer distribution archives. Original
code is MIT; Composer, PHP and payloads retain their own licenses.

```nix
backend.makePackage {
  name = "example/library";
  version = "1.0.0";
  payload = preparedTree;
  autoload."psr-4"."Example\\" = "src/";
  require.php = ">=8.0";
  license = "MIT";
}
```

`backend` is `import (inputs.composer-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
The payload is the package root. Generated composer.json replaces any existing
one; `autoload`, `require`, `bin`, `description` and `license` supply package
metadata. The default license is proprietary, not an inferred payload license.
Versions are three-component releases with an optional prerelease suffix.

Actual `composer archive` creates package.zip; wrapper timestamps are normalized
for reproducibility. Build-time plugins and scripts are disabled. Consumers can
point Composer's native artifact repository at a directory of these ZIP files,
or publish suitable distribution metadata through a Composer repository.
Registry publication, credentials and application environment policy are external.

This distributes prepared files, rather than making arbitrary nixpkgs programs
PHP-compatible. PHP versions, required extensions and native ABIs remain producer
responsibilities. No Nix client, daemon, database or relocation is added.

`nix flake check -L` runs Composer inside QEMU with network access disabled and
Packagist disabled: install from local artifacts, load a class through the actual
Composer autoloader, upgrade, check platform requirements and remove. It verifies
that the package and class are unavailable after removal. Native PHP extensions
and additional platforms need their own compatibility tests.
