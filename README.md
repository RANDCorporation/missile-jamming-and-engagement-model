# Missile Jamming and Engagement Model (MJEM)

## Introduction

The Missile Jamming and Engagement Model (MJEM) estimates measures of performance and a measure of effectiveness for an air-launched missile engagement against a target as a function of position, navigation, and timing (PNT) information available to the missile. MJEM was developed to help assess the dependence of missiles on airborne or space-based signals for success in engagements under conditions where those signals may be jammed or otherwise degraded.

This model analyzes the accumulation of position errors from multiple sources including GPS jamming, inertial navigation system (INS) drift, target location errors (TLE), and in-flight target updates (IFTU) under radio frequency jamming conditions. The model outputs include jamming ranges, RMS position errors, and probability that the target remains within the seeker's field of regard (FOR).

## Installation

### Requirements

- Python 3.11 or higher
- Required packages:
  - numpy
  - matplotlib

### Setup

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install numpy matplotlib
   ```

## Usage

MJEM is designed to run batch analyses using a CSV "run matrix" file containing input parameters for multiple scenarios.

### Basic Usage

1. **Prepare your input file**: Create a CSV file with the required input parameters. See `MJEM_RunMatrix_ReportExamples.csv` for the correct format and an example with unclassified parameters.

2. **Configure the code**: Edit `main_mjem.py` to specify your input and output filenames:
   ```python
   RunMatrixFilename = "MJEM_RunMatrix_ReportExamples.csv"
   ResultsFilename = "MJEM_Results_ReportExamples.csv"
   FigFilename = "MJEM_Results_ReportExamples.jpg"
   ```

3. **Run the model**:
   ```bash
   python main_mjem.py
   ```

4. **Review results**: The model generates:
   - A CSV file with numerical results (MOPs and MOE)
   - JPG figures showing position error over time for each case (saved in `Figures/` directory)

### Input Parameters

The input CSV file must include the following columns for each run case:
- Case number and description
- Missile velocity, launch range, seeker parameters
- Target location error and evasive maneuver parameters
- GPS parameters (velocity, received power, jamming threshold, CRPA antenna characteristics)
- IFTU parameters (latency, antenna characteristics, frequency hopping gain)
- Jammer parameters (GPS and IFTU jammer ERP)
- Flags for GPS denied and IFTU denied scenarios

### Output

For each case, MJEM produces:
- **GPS Jamming Range** (km): The range at which GPS signals are jammed
- **IFTU Jamming Range** (km): The range at which IFTU signals are jammed
- **RMS Position Error** (km): Root mean square position error at seeker acquisition
- **Probability Target is in FOR**: Probability the target remains within the seeker's field of regard
- **Figure**: Visualization showing position error accumulation over time and range

## Code Structure

The implementation consists of four Python modules:

1. **brien_iftu.py**: Defines the `InFlightTargetUpdate` class that implements mathematical formulas for IFTU contributions to RMS position error.

2. **brien_ins.py**: Defines the `InertialNavigationSystem` class that implements mathematical formulas for INS contributions to RMS position error.

3. **brien_mjem.py**: Defines the main `MJEM` class representing a complete missile engagement. Includes member objects for IFTU and INS, and methods to calculate GPS/INS jamming ranges, flight times, position error accumulation, and MOPs/MOE.

4. **main_mjem.py**: The code entry point. Reads the input CSV run matrix, processes each case, generates figures, and writes results to output files.

## Data

An example input file `MJEM_RunMatrix_ReportExamples.csv` is included with unclassified parameters demonstrating six scenarios:
- P(Y) Code GPS with various antenna configurations
- M Code (Spot) GPS with phased array antennas
- GPS denied scenarios
- IFTU denied scenarios
- Different target location error (TLE) values

Users must create their own CSV input files following this format for their specific analysis cases.

## Project Information

This research was conducted for two projects:
1. Commissioned by HAF A2/6L as part of fiscal year 2024 project "Ensuring Successful Electromagnetic Operations in a Complex, Contested, and Congested Electromagnetic Environment"
2. Commissioned by SSC/SZ-BC as part of fiscal year 2024 project "Kill Chain Analysis and Support to the USSF and USAF"

Both projects were conducted within the Force Modernization and Employment Program of RAND Project AIR FORCE (PAF).

This work was originally shared with the Department of the Air Force on September 26, 2024. It was published to the rand.org website on March 7, 2025

## References

For detailed methodology, mathematical formulations, and analysis results, see:

Brien Alkire. *Missile Jamming and Engagement Model*. RAND Corporation, RR-A3150-2, 2025. https://www.rand.org/pubs/research_reports/RRA3150-2.html

The report provides comprehensive background on:
- Link budget analysis for GPS and IFTU signals under jamming
- Position error accumulation modeling
- Probability calculations for target acquisition
- Example scenarios and sensitivity analyses

## Assumptions and Limitations

- The model assumes basic probability and statistics knowledge and familiarity with link budget analysis
- Users should have the technical skills to create input CSV files and interpret graphical and numerical results
- No graphical user interface is provided; operation requires direct editing of Python files and command-line execution
- The model is designed for long-range air-launched missile scenarios in RF jamming environments

## Copyright and License

Copyright (C) 2025 RAND Corporation. This code is made available under the MIT license. See LICENSE file for details.

## Author and Citation

**Author:** Brien Alkire (brien@rand.org), RAND Corporation

**To cite this software:**

Brien Alkire. *Missile Jamming and Engagement Model*. RAND Corporation, RR-A3150-2, 2025. https://www.rand.org/pubs/research_reports/RRA3150-2.html

**BibTeX:**
```bibtex
@techreport{Alkire2025MJEM,
  author = {Alkire, Brien},
  title = {Missile Jamming and Engagement Model},
  institution = {RAND Corporation},
  year = {2025},
  type = {Research Report},
  number = {RR-A3150-2},
  url = {https://www.rand.org/pubs/research_reports/RRA3150-2.html}
}
```

---

