# REHS 2024
This project is part of the Research Experience for High School Students (REHS) program. 

Developed by Samhita Lagisetti and Ethan Jin, under the supervision of Dr. Martin Kandes.

Click [this link](https://github.com/user-attachments/files/16488524/Ethan.J.Samhita.L.Martin.K.REHS.2024.pdf) to download a PDF of the project research poster.


# Description
On the Expanse supercomputer, users have implemented thousands of software modules. These modules are tracked within various usage logs, each one containing hundreds of thousands of lines. Our goal was to sift through this data using Pandas (a Python library) and answer different queries about it, including but not limited to:

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

# Dependencies
This project requires two Python packages: Pandas and Matplotlib. We recommend managing your environment through [Conda](https://docs.conda.io/projects/conda/en/stable/) or [Miniconda](https://docs.anaconda.com/miniconda/).

# Using the Code
This project has several features. User input is made possible by the argparse package, which creates a command-line interface in your local terminal. Start each query with `python parse_data.py`. We suggest viewing the project through Visual Studio Code.

## Customize Database Input
By default, the log files are stored within a folder named "moduleUsage": `module_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), 'moduleUsage'))`

If you have stored the files to a different path, replace `moduleUsage` with the directory name. Alternatively, you can change the moduleUsage folder itself by taking out or adding files.

## Running it directly
If you run the file directly, the code will parse all the data from every module usage log and output it into a neat dataframe. From left to right, the headings are:
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
To save the dataframe to a file, type `"-s" or "--save"`. The provided formats are .csv and .parquet.
## Find unique modules/users
One of the core functionalities is sifting through the data to find unique users and modules.

Hashing option: despite having the same name, some modules differ depending on their origin. Automatic 7-digit hashing is included by default, but if you want to be more specific and generate an MD5 hash for each module based on its path, just type `"--hash"`.
### Display as a List
Queries:
  - `"-users" or "--unique_users"` --> Display unique users
  - `"-mod" or "--unique_modules"` --> Display unique modules
  - `"-f" or "--find"` --> Find specific module/user
  - `"--spack"` --> Search for specific Spack instances
  - `"--spack_root"` --> Search for modules associated with specific Spack root module(e.g. cpu/0.17.3b)

Example list:

![Screenshot 2024-07-28 at 11 25 13 PM](https://github.com/user-attachments/assets/e02837ea-0f3b-493b-9cea-223228d3cb72)

![Screenshot 2024-07-28 at 11 25 21 PM](https://github.com/user-attachments/assets/8532a912-941b-4bcf-b03d-4c5de803555c)
### Display as a Pie Chart
To display the modules/users on a pie chart, you must still type the aforementioned queries(e.g. "-users" and "-mod"). However, our project offers robust options to customize the graph.

Queries: 
  - `"-plt" or "--plot"` --> Plot data
  - `"-t" or "--top"` --> Number of top modules/users to visualize. Defaults to five.
  - `"-all"` --> Include all values in the pie chart

Please remain patient while the graph is being generated. The runtime depends on the number of logs you are parsing through.

Example chart:

![cpu_table](https://github.com/user-attachments/assets/97ec0059-fee8-4824-924a-044f448e785c)


# Acknowledgements
We would like to thank UCSD and SDSC for hosting this amazing program. 

Additionally, our work wouldn't be possible without the efforts of program coordinator Ange Mason and consistent guidance from our mentor, Dr. Kandes.

