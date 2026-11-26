# Reproduce the checks

Run the finite truth-set replay and archive verifier from the repository root.

```sh
python3 -I verification/src/replay.py
python3 -I scripts/verify_repository.py
```

The replay enumerates all 256 Boolean matrices on three bits, with and without the matrix padding. It computes prefix-maximal truth sets, stable ranks and guarded maxcon projection, with and without an extra middle-tier source. It also tests the two exact examples in the offline explorer. These checks are finite. [Replay output](verification/logs/replay.txt) · [Build the paper](paper/BUILD.md) · [Visual source](visualization/README.md)
