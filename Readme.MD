# NASHDetection

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Description

Welcome to the NASHDetection repository! 
This project is entitled "NASHDetection: A natural language processing method for identifying patients with metabolic associated steatohepatitis using clinical notes". 



 **Introduction**: 

This is an internally validated, natural language processing-based algorithm for detecting patients with non-alcoholic steatohepatitis from clinical notes documented in electronic health records systems. An abstract detailing the methods for developing and validating this algorithm have been accepted for presentation at the American College of Gastroenterology 2023 Annual Ameeting. A brief description of the algorithm's rationale and underlying methods follow.

Background, Rationale:
Nonalcoholic fatty liver disease (NAFLD) is the most common chronic liver disease in western countries and is growing in prevalance around the world. Nonalcoholic steatohepatitis (NASH) is an inflammatory subtype of NAFLD that leads to progressive liver injury and liver failure. The diagnosis of NASH typically requires an expert assessment of all available clinical data, which sometimes includes liver histopathology.
Diagnoses in electronic health records (EHR) systems are commonly coded using systems like ICD-10. However these coding systems have well known inaccuracies, necessitating more accurate methods of disease ascertainment. Clinical notes authored by expert physicians are a superior source of truth on the presence of NASH, but have historically been underutilzed due to the absence of valdiated natural langauge processing (NLP) algorithms.
We developed an algorithm for developing a retrospective, EHR-based cohort of patients with NASH, and identifying the earliest date at which this diagnosis was made within the EHR system (i.e. index date)



 **Features**: 
 
The input for this algorithm is an outpatient clinical note that has been authored by a board-eligible/board-certified hepatologist.
This algorithm has been internally validated at the University of California, San Francisco (UCSF) but has not yet been tested at other centers.
This algorithm should only be used on patient encounters prior to liver transplantation.
Method:
Outpatient clinical notes authored by hepatology physicians at UCSF were extracted using queries of an EHR database. These notes had been subjected to machine redaction of protected health information prior to the development of our algorithm.
First, we identified the ‘Assessment and Plan’ sectin of these notes using regular expressions and MedSpacy sectionizer tool.
Next, we identified mentions of NASH or its synonyms, using regular expressions and named entity recognition. The detection of NASH in this section was interpreted as evidence that this diagnosis exists as of the date that the corresponding note was written.
This method was applied to all notes across the patient timeline. The earliest date at which NASH was asserted in a note is inferred as corresponding to the index date.


 **Installation**: 
Check, reuirements.txt and installation and dependencies.txt files

## Installation

Here are the steps to install and set up the project locally:

1. Clone the repository: `https://github.com/rwelab/NASHDetection.git`
2. Navigate to the project directory: `cd NASHDetection`
3. Install dependencies: `pip install` or `yarn install` (depending on the package manager you use)

## Usage

```bash
# Run the script
python NASH_Detection.py #algorithm to detect NASH mentions

```
##Sample data

The algorithm expects unstractured data with ids in comma seperated (.csv) file.
Example
Id,Note_text
P01,"The patient is consulted for....."

## Contributing

We welcome contributions from the community! If you want to contribute to the project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix: `git checkout -b feature/your-feature-name`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Submit a pull request to the `main` branch.

Please ensure that your code follows the project's coding style and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

