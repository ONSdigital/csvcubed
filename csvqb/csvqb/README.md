# CSVqb

A tool to generate qb-flavoured CSV-W cubes from regular CSVs.

## Command Line Interface

```bash
Usage: csvqb [OPTIONS] COMMAND [ARGS]...

  CSVqb - a tool to generate qb-flavoured CSV-W cubes.

Options:
  -h, --help  Show this message and exit.

Commands:
  build  Build a qb-flavoured CSV-W from a tidy CSV.
```

### Build

Build the qb-flavoured CSV-Ws from an *info.json V1* file.

```bash
Usage: csvqb build [OPTIONS] TIDY_CSV_PATH

  Build a qb-flavoured CSV-W from a tidy CSV.

Options:
  -c, --config CONFIG_PATH        Location of the info.json file containing
                                  the QB column mapping definitions.
                                  [required]
  -o, --out OUT_DIR               Location of the CSV-W outputs.  [default:
                                  out]
  --fail-when-validation-error / --ignore-validation-errors
                                  Fail when validation errors occur or ignore
                                  validation errors and continue generating a
                                  CSV-W.  [default: fail-when-validation-
                                  error]
  --validation-errors-to-file     Save validation errors to an `validation-
                                  errors.json` file in the output directory.
                                  [default: False]
  -h, --help                      Show this message and exit.
```