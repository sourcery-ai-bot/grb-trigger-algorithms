
Hello and welcome! 

This is a code repository for the paper:
# Gamma-ray burst detection using Poisson-FOCuS and other trigger algorithms
_Authors: 
Giuseppe Dilillo, 
Kes Ward, 
Idris Eckley, 
Paul Fearnhead, 
Riccardo Crupi,
Yuri Evangelista,
Andrea Vacchi,
Fabrizio Fiore_

The paper deals with the problem of detecting GRBs. In particular we use 
Poisson-FOCuS, a novel anomaly and changepoint detection technique for 
Poisson-distributed count time series. 
Make sure also to give the look at the papers where 
FOCuS and FOCuS-Poisson were first introduced [1][2]!

## Data

You can download the data used in this research from [Zenodo](https://doi.org/10.5281/zenodo.8334676).

## Setup

### Requirements
1. Python and few external packages, see section section "Environment creation".
2. To run the C code of this repository you will need cmake and a compiler (such as GCC).

### 1. Download
First you must download the data and the present repository.
For downloading the data go to Zenodo link above and download all the files there,
from the page's bottom panel.
To clone the repository, you can use git. 
Run from your terminal at appropriate location:

`git clone https://github.com/peppedilillo/grb-trigger-algorithms.git`

If you have no git, you can download the repository clicking on the green
button on the top right of this page and then clicking on `Download zip`.

### 2. Environment creation
We provide an environment file to easily setup a python anaconda environment.
To install this environment, move to the repository's local folder and run:

`conda env create -f environment.yml`

If everything went fine you should now be able to see an environment called
`grb-trigger-algorithms` in your environment list, which you can get using
`conda env list`.

If you are not using anaconda you can still use  `environment.yml` to find all 
the packages needed to run the python code of this repo.

### 3. Everything in its right place 

Now we do put the data in their default location.
This will make it easier to run the scripts.
Move the datasets you downloaded from Zenodo in the `grb-trigger-algorithm\data\`
data folder, then unzip the file `simulated_dataset_compeff.zip`.
The folder structure should look something like this:

```
grb-trigger-algorithm
|- .gitignore
|- environment.yml
|- README.md
|- grb-trigger-algorithm
| |- data
| | |- \README.md
| | |- simulated_dataset_grb180703949.fits
| | |- simulated_dataset_grb120707800.fits
| | |- gbm_dataset_50to300keV_binned16ms_20171002_20171009.zip
| | |- simulated_dataset_compeff
| | | |- pois_l4_n2048_0000.txt
| | | |- ..
```

### 4. Compiling the C implementations

We provide C implementations for Poisson-FOCuS and a benchmark algorithm emulating
the one from Fermi-GBM. To use this programs you need to compile them.
We provide CMake files for this purpose.

For compiling the C implementation of Poisson-FOCuS:
1. Move to `grb-trigger-algorithm/grb-trigger-algorithm/algorithms_c/pfocus_c/`
2. In there, create a directory called `cmake-build-debug` and another called `cmake-build-release`.
3. Move to the `cmake-build-debug` folder and (assuming cmake is in your PATH) run `cmake ..  -D CMAKE_BUILD_TYPE=Debug`.
4. Now run `cmake --build . --config Debug`.
3. Move to `../cmake-build-release` folder and run `cmake ..  -D CMAKE_BUILD_TYPE=Release`.
4. Now run `cmake --build . --config Release`.

This will create executables in you debug and release folders called `pfocus` and `pfocus_compeff`.
The difference between the debug and release versions is that the debug one will print a control string
at each algorithm iteration.

Repeat the same for the benchmark, which is located in the folder `grb-trigger-algorithm/grb-trigger-algorithm/algorithms_c/benchmark/`.

-----

And.. You are set! Make sure to give a look at what's inside `grb-trigger-algorithm`,
you will find more instructions in there.

## Uninstalling

To uninstall delete the repository local folder.
If you installed our conda environment you can uninstall it with:

`conda remove -n mescal --all`
## Bibliography

[1]: Ward, Kes, et al. "Poisson-FOCuS: An efficient online method for detecting count bursts with application to gamma ray burst detection." Journal of the American Statistical Association (2023): 1-13.

[2]: Romano, Gaetano, et al. "Fast online changepoint detection via functional pruning CUSUM statistics." Journal of Machine Learning Research 24 (2023): 1-36.

