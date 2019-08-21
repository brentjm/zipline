# Investment testing using zipline
A Python enviroment to test investing ideas using the zipline library
in Jupyter Lab notebooks.

## Overview
* *Dockerfile*
  * Uses the base Debian (stretch) OS
  * Installs Python, zipline, jupyter and some math libraries
  * CMD runs jupyter notebook
* *docker-compose.yml*:
  * Creates the base Debian zipline service
  * Opens port 8888
  * defines a bind volume to store jupyter notebook

## Getting started
1. clone this repository
2. run docker-compose
`$docker-compose up -d`
3. Open browser to localhost:8888

## Customization
1. Save Jupyter notebooks in the bind volume

# Author

**Brent Maranzano**

# License

This project is licensed under the MIT License - see the LICENSE file for details
