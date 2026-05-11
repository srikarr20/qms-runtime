# Benchmarks

Benchmarks are protocol-level orchestrations over QMS layers.

`frozen/` contains immutable protocol references such as QMCTB-01 v1.0.

`evolving/` contains benchmark candidates and later versions such as QMCTB-02,
QMCTB-03, and QMCTB-04 until a specific version is frozen.

Benchmark runners may compose layer APIs, but benchmark code must not collapse
foundation, measurement, acquisition, diagnostics, and control into one layer.

