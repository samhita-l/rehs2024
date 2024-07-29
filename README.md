# REHS 2024
Part of the Research Experience for High School Students (REHS) program. Developed by Samhita Lagisetti and Ethan Jin under the supervision of Dr. Martin Kandes

# Description
Many users have implemented thousands of software modules on the Expanse supercomputer. These modules are tracked within various module usage logs, each containing hundreds of thousands of lines. Our goal was to sift through this data using Pandas (a Python library) and answer different queries about it, including but not limited to:

  1. How often (or frequent) are the different Spack instances being used? i.e., how often are these module names loaded?
     - cpu/0.17.3b
     - gpu/0.17.3b
     - cpu/0.15.4
     - gpu/0.15.4
    
  2. How many unique users were using software module environment on Expanse?
  
  3. What are the top-10 most popular software modules from the different Spack instances currently deployed on Expanse? You likely need to use the SPACK_ROOT variables here to help delinate which Spack instance a software module is located.
     - SPACK_ROOT=/cm/shared/apps/spack/0.17.3/cpu/b
     - SPACK_ROOT=/cm/shared/apps/spack/0.17.3/gpu/b
     - SPACK_ROOT=/cm/shared/apps/spack/cpu
     - SPACK_ROOT=/cm/shared/apps/spack/gpu
    
  4. How many Singularity users are there on Expanse? e.g., see module name 'singularitypro'.


# Install
Make sure Git is installed in your command-line interface. Then, run `git clone https://github.com/samhita-l/rehs2024.git` in the terminal to clone this project to your local device. 

# Using the Code
This project has several features. User input is made possible by the argparse module, which creates a command-line interface in your local terminal. Start each query with `python parse_data.py`. We suggest viewing the project through Visual Studio Code.

## Running it directly
If you run the file directly, the code will parse all the data from every module usage log and output neatly into a simple dataframe. From left to right, the headings are:
  - Module
  - Version
  - Hash
  - Username
  - Path
  - Effective User ID (EUID)
  - Effective GID (EGID)
  - Date
  - Time
  - Unix time
## Save dataframe
To save the dataframe to a file, type "-s" or "--save" and the file type, either in csv or parquet format.
## Find unique modules/users
One of the core functionalities is sifting through the data to find unique users and modules.

Hashing option: some modules, despite having the same name, differ depending on their origin. Automatic 7-digit hashing is provided, but if you want to provide each module with an MD5 hash based on its path, just type "--hash".
### Display as a List
Queries:
  - "-users" or "--unique_users" --> Display unique users
  - "-mod" or "--unique_modules" --> Display unique modules
  - "-f" or "--find" --> Find specific module/user
  - "--spack" --> Search for specific Spack instances
  - "--spack_root" --> Search for modules associated with specific Spack root module(e.g. cpu/0.17.3b)

Example list:
`Modules
cpu/0.15.4                                 86089
cpu/0.17.3b                                83815
gcc/10.2.0                                 55165
cmake/3.18.2                               32077
openmpi/4.0.4                              31234
openblas/0.3.10-openmp                     18776
gaussian/16.C.01                           16929
gnuplot/5.2.8                              16327
gmp/6.1.2                                  16228
mpfr/4.0.2                                 16212
                      .....
                      
There are 440 unique modules. The complete list is shown above, ranked by how many times each module appears.
The most frequent module is cpu/0.15.4 with 86089 occurrences.`

### Display as a Pie Chart
To display the modules/users on a pie chart, you must still type the aforementioned queries(e.g. "-users" and "-mod"). However, our project offers robust options to customize the graph.

Queries: 
  - "-plt" or "--plot" --> Plot data
  - "-t" or "--top" --> Number of top modules/users to visualize. Defaults to five.
  - "-all" --> Include all values in the pie chart

Example chart:
![cpu_table_all](https://github.com/user-attachments/assets/f2cdc65d-4d1f-4e8b-b9b4-a7492bd69be3)

# Acknowledgements
This entire project wouldn't be possible without the efforts of program coordinator Ange Mason and consistent guidance from our mentor, Dr. Kandes. Additionally, we would like to thank UCSD and SDSC for hosting this amazing program!

