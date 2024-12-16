# Advanced Network Automation

*Automating network configurations with Jinja2 templates, YAML, and robust CI/CD integration.*

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)

## Introduction

Advanced Network Automation is designed to streamline network device configurations using Jinja2 templates and YAML files. The project incorporates tools like J2Lint for syntax checking, Containerlab for network simulation, and Jenkins for continuous integration, aiming to enhance efficiency and reduce manual errors in network management.

## Features

- **Jinja2 Templates**: Facilitate dynamic and reusable network configurations.
- **YAML Configuration**: Enable straightforward and human-readable configuration files.
- **Automated Syntax Checking**: Utilize J2Lint to ensure template accuracy.
- **Network Simulation**: Employ Containerlab for testing network topologies.
- **CI/CD Integration**: Integrate with Jenkins for automated testing and deployment.
- **Self healing automated network troubleshooting**: Integrated Slack API for real-time notfiications.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/coflin/Advanced-Network-Automation.git

2. **Navigate to the Project Directory**:
   ```bash
   cd Advanced-Network-Automation
   ```
## Usage

Start the Containerlab topology:
```bash
sudo containerlab deploy -t topology.yaml
```

## Project Structure
```bash
Advanced-Network-Automation/
├── configs/
│   ├── example_config.yaml
│   └── ...
├── templates/
│   ├── example_template.j2
│   └── ...
├── scripts/
│   ├── deploy.py
│   └── validate.py
├── tests/
│   ├── test_deploy.py
│   └── ...
├── requirements.txt
├── README.md
└── ...
```

## Contributing
Contributions are welcome! Please follow these steps:

Fork the repository.
Create a feature branch 
```bash
git checkout -b feature-branch-name
```
Commit your changes 
```bash
git commit -m "Add new feature"
```
Push to your fork 
```bash
git push origin feature-branch-name
```
Open a Pull Request.



