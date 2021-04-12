# Simulation-Based Analysis of COVID-19 Spread Through Classroom Transmission on a University Campus

This repository presents the source code for analyzing the airborne COVID-19 transmission risk associated with holding in-person classes on university campuses.

<ins>***This model can be replicated by other universities to help mitigate Covid-19 cases***</ins>.

## Data Source

This project used the campus and students' registration of a large university in the paper. Here, we provided a synthetic dataset in [/Dataset](https://github.com/ANRGUSC/covid-university-simulation/tree/main/Dataset). The code requires information regarding the classrooms, such as their location name, area, and air change rate. Furthermore, the code needs information regarding the students' schedule for the semester, such as their courses and the location and time of those courses. All of the required datasets can be generated via the synthetic generator provided in the source codes. 

## Instructions for running the codes

The requirements.txt file contains the modules needed to run these scripts and can be installed by running the following command in the terminal:
* pip install -r requirements.txt

## Running **generate_synthetic_data.py**

This main file can be found in the [/source_code](https://github.com/ANRGUSC/covid-university-simulation/tree/main/source_code) folder.

Input:
- Classroom parameters
- Students' schedule parameters

Output:
- Classroom synthetic dataset
- Students' schedule dataset

## Running **run_infection_prob.py**

This main file can be found in the [/source_code](https://github.com/ANRGUSC/covid-university-simulation/tree/main/source_code) folder.

Input:
- The campus and students' registration dataset
- Infection model parameters
- Policies parameters (Hybrid scheduling, mask wearing, occupancy reduction)

Output:
- Histogram plot and csv file of the infection probability distribution of the students



