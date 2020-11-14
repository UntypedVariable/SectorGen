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
  * `-m <vn,so,hs>`, `--mode <vn,so,hs>`
  * `-d`, `--draw`
  * `-i <hex_location>`, `--inspect <hex_location>`

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