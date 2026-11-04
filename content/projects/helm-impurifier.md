# helm-impurifier

Package Nix-built templates and prepared resources as native Helm charts.
Original code is MIT; Helm, Kubernetes and chart payloads retain their licenses.

```nix
backend.makeChart {
  name = "example";
  version = "1.0.0";
  templates = preparedTemplates;
  values.image = "registry.example.org/application@sha256:...";
}
```

`backend` is `import (inputs.helm-impurifier + "/nix") { inherit pkgs; coreSrc = inputs.impurifier; }`.
`templates` supplies the chart's template directory. Native v2 Chart.yaml and
values.yaml are generated from name/version, `description`, `appVersion` and
`values`; JSON is used as valid YAML. `dependencies` is a list of already-built
subchart archive paths to vendor into charts/. There is no dependency fetch.
Upstream helm lint and helm package validate and pack the chart, then archive
headers are normalized for reproducibility. The output is name-version.tgz.

Nix can produce chart templates, configuration and other templated resources.
Container image building is a separate OCI artifact contract; pass concrete
image references through values. Consumers use normal Helm install/upgrade/
rollback/uninstall. This backend does not manage clusters, publish images/charts,
store registry credentials or require target Nix. Signing/provenance generation
must follow archive normalization and remain external producer operations.

`nix flake check -L` uses actual Helm against a real k3s Kubernetes API in QEMU.
It installs a chart, verifies its managed ConfigMap, upgrades and verifies the
new value, rolls back and verifies the original value, then uninstalls and
requires the object to be gone. The fixture is an agentless control plane and
does not claim container scheduling, image pulling or application execution.
