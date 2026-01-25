# Matchmaking System Visualiser
## Overview
This is a Final Year Computer Science Project that implements the theoretical matchmaking system proposed by J. Alman and D. McKay, “Theoretical Foundations of Team Matchmaking,” In Proceedings of the 16th Conference on Autonomous Agents and MultiAgent Systems, pp. 1073-1081, 2017.
This codebase implements the Unrestricted and Time-Sensitive variants of the system, including the option of using a heuristic to speed up the process, while still guaranteeing optimality within a given margin.
There are two ways to interact with the system: 
* A command-line interface (CLI) which allows the user to access all the features of the matchmaking system through the terminal
* A streamlit powered web application which provides a user-friendly graphical interface to interact with the system, visualise the matchmaking process, and see the results in an intuitive way.

## System Configuration
Regardless of the interface used, the configuration of the matchmaking system remain the same, including the customisation of the parameters of the imbalance and priority functions specified in the paper. The user can specify the following parameters:
- **Mode:** Unrestricted or Time-Sensitive.
- **Team Size (k):** Number of players per team (1-5).
- **Fairness Norm (p):** Norm used to measure fairness (≥1.0).
- **Uniformity Norm (q):** Norm used to measure uniformity (≥1.0).
- **Fairness Weight (α):** Weight given to fairness in matchmaking (>0.0).
- **Queue Weight (β):** Weight given to queue time in Time-Sensitive mode (>0.0).
- **Matchmaking Approach:** Option to use the heuristic of reducing the skill window to 2k-1 for faster matchmaking.
- **Is Recording:** The CLI option to record the matchmaking process to then view in the terminal.

## How to Use
This project was made using Python 3.12. To set up the environment and install the dependencies, follow these steps:
1. Clone the repository to your local machine.
2. Run the following Makefile commands, or copy the contents of the command to set up the environment and install dependencies:
   ```
   make init
   make requirements-all
   ```
3. To run the command-line interface, use:
   ```
   make run-cli
   ```
4. To run the web application, use:
   ```
   make run-app
   ```
Alternatively, the web application can be accessed directly on the web using the following link:
   [Matchmaking System Visualiser Web App](https://fyp-278985.streamlit.app/)

