# maven-impurifier

Publish prepared JVM artifacts in a native Maven repository layout. MIT licensed.
Payloads and upstream SDKs retain their own licenses.

```nix
backend.makeArtifact {
  groupId = "org.example";
  artifactId = "library";
  version = "1.0.0";
  artifact = preparedJar;
  dependencies = [{ groupId = "org.example"; artifactId = "helper"; version = "2.0.0"; }];
  classifiers.sources = preparedSourcesJar;
}
```

`backend` is `import (inputs.maven-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
The output is a repository tree containing the artifact, XML-escaped POM,
classifier artifacts and SHA-1/SHA-256/SHA-512 compatibility sidecars. Merge
separate outputs into a feed without overwriting immutable coordinates.
`packaging` defaults to `jar`; classifiers use that extension. `description`
supplies POM metadata. Dependencies accept groupId, artifactId, version, scope,
type, classifier and optional. Advanced POM features and snapshot/dynamic-version
metadata are not implemented. Publish immutable releases.

Maven, Gradle and compatible clients can consume the directory as a repository.
The artifact is copied unchanged; it may be built by Nix with any suitable JVM
toolchain. Target bytecode and native-library ABI compatibility remain producer
responsibilities. No Nix runtime, recompilation or relocation is introduced.
Repository hosting, credentials and detached signing are external operations.
Checksums are compatibility metadata, not a substitute for repository trust.

`nix flake check -L` uses actual Gradle inside QEMU, offline, to resolve a JAR
and its transitive POM dependency, compile and execute a consumer, select a new
version and execute it again. Removing the artifacts and native dependency cache
makes resolution fail. Gradle is the tested Maven-format consumer; this does not
claim every Maven plugin or repository server has been tested. Consumer caches
and build outputs follow their native retention rules.
