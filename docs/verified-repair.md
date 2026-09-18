# Verified repair scope

The starting source was `3d457ec3001c56ab352548aa356dfadcf960f037`. The bundled example commands completed,
but there was no automated assertion suite. Bounded synthetic input probes
exposed the defect addressed here.

Report same-video positive-duration overlaps with explicit policy and opt-in strict gate; keep report exit behavior.

New regression tests failed before the repair. After the change, `make verify`
passed 4 test methods, including independent result oracles and negative
command-line cases. Every original documented sample command was rerun. Test
counts are methods; parameterized inputs are not inflated into separate tests.

The tests use the standard library and synthetic fixtures. They do not claim
comprehensive schema validation, real model quality, external evidence quality,
or production readiness. CI repeats the discoverable verification command.
