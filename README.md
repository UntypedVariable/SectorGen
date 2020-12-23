# SectorGen

Procedural Sector Generation for Traveller.

https://github.com/UntypedVariable/SectorGen


## Requirements

* python3
* Python Imaging Library (PIL)


## Operation

* command line: `python3 __main__.py <arguments>`
* arguments:
  * `-h`, `--help`
  * `-g`, `--generate`
  * `-d`, `--draw`
  * `-i <hex_location>`, `--inspect=<hex_location>`

### generate & mode

* `--generate` creates a new sector based on the settings in config
* `--mode` requires the `--generate` argument to be called
  * `--mode` _is not currently functional_


### draw

* Quadrant maps are enumerated and named **clockwise**
* Sector and Subsector maps are left-to-right, top-to-bottom


### inspect

* entering "test" instead of a hex location provides a test-output
* leading zeroes are required. example: `-i 0101`
* the inspector can take several arguments
  * `-v`, `--verbose` provides an extended output
  * `-s`, `--selection` changes which part of the hex to output
    * `c`, `complete`: outputs the complete system `!!not yet implemented`
    * `s`, `star`: outputs information on the system's star(s) `!!terse output only`
    * `mw`, `mainworld`: outputs information on the system's Mainworld (default)
    * `b`<n>, `band`<n>: outputs information on a specific object `!!not yet implemented`
    