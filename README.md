BinSE: Accurate and Efficient Cross-Version Binary Code Search with Compilation Resilience

The repository is structured in the following way:
1. Source Code of BinSE
  - FunctionFiltering: BinSE eliminates irrelevant target functions and identifies potentially similar candidate target functions.
  - Preprocessing: BinSE converts each binary function into a normalized CFG to represent its meaningful semantics to diminish the discrepancies in instructions caused by version change.
  - CrossVersionFunctionSearch: BinSE searches for the target function, which corresponds to the query function across different versions.

2. Datasets of BinSE
