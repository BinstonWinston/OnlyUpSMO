[!WARNING]
Some knowledge of Linux, Python, and Bazel is required to use this generator. If you just want to play this mod, try the fixed seed version here for the simplest installation.

# SMO OnlyUp Stage Generator
Components
* **OnlyUp Stage Generator** (`src/generator`): Procedural stage generation for OnlyUp-style stages, but could be adapted to other styles as well
* **Stage Creation Library** (`src/stage`): utilities and wrapper classes for simplifying stage byml writing
* **Collision Utilities** (`src/file_format/kcl.py`): check object collisions, choose random positions on object surface with given constrains (e.g. normal is roughly upwards and there is enough space for mario to stand)


## Running
### Pre-requisites
* Linux
* [Bazel](https://bazel.build/) (>=6.3.2)
* RomFS dump from your copy of SMO
  

```
bazel run //src:generate_stage -- -i /path/to/smo/romfs -o /path/to/output/dir -s YOUR_SEED_STRING
```
[!IMPORTANT]
All paths must be absolute. Bazel runs in a sandbox so paths relative to the current directory will not work correctly.

* `-i`, `--input_romfs_path` A romfs dump of SMO obtained from your copy of SMO, used for reading object collisions
* `-o`, `--output_romfs_path` Output directory to place generated stage and object files
* `-s`, `--seed` A string used to seed the random generation. Similar to MineCraft, the same seed will always produce the same output

## Stage Creation Library
At a high-level, the stage creation library (`src/stage`) allows for simple creation of procedural stages without having to mess with byml details. The library is not complete, but contains enough OnlyUp features like moving objects and timers, and should (hopefully) not be too difficult to extend to new use cases.

This library uses factory functions (`src.stage.ObjectFactory`) to create higher-level wrapper classes (`src.stage.Object`) which provide a less error-prone way of interfacing with stage data. The wrapper classes are then converted to protobuf types (see `src/stage/proto`) to automate checking field name and types. This protobuf is then converted to a raw Python dictionary and finally converted to the stage map byml.

For usage examples of the stage creation library, see `src/generator`.

## Third-Party Libraries
* [sarctool/sarclib](https://github.com/aboood40091/SARC-Tool)

## Special Thanks
* SMO Modding Discord for help with a bunch of random questions