# SoilSensorEmail System

## Overview

The `SoilSensorEmail` system is a Raspberry Pi-based project designed to monitor soil moisture levels of a plant and send email notifications when watering is needed. This project integrates a soil moisture sensor with a Raspberry Pi, implements email notifications using Python's `smtplib`, and provides a user-friendly Tkinter-based GUI for real-time monitoring and schedule management. The system was developed using Agile methodologies, with version control managed via Git and GitHub.

## Features

- **Soil Moisture Monitoring**: Uses a digital soil moisture sensor (FC-28) connected to Raspberry Pi GPIO pin 4 to detect whether the soil is wet or dry.
- **Email Notifications**: Sends email alerts at scheduled times (default: 07:00, 10:00, 13:00, 16:00) to notify the user of the plant's status ("Water NOT needed" or "Please water your plant").
- **Tkinter GUI**: Provides an interactive interface to display current status, last check time, next scheduled check, email status, and manage notification schedules.
- **Diagnostics**: Includes a diagnostic feature to test sensor and email functionality.
- **Fallback Mode**: Supports a fallback mode if the sensor is unavailable, allowing the GUI to function without hardware.

## Screenshots

### GUI Showcase

![SoilSensorEmail GUI](https://github.com/Nickory/Project2_2025/blob/main/show.png)
*The Tkinter-based GUI displaying the current soil moisture status, schedule, and email status.*

### Physical Setup

![Physical Setup](https://github.com/Nickory/Project2_2025/blob/main/setup.png)
*The Raspberry Pi connected to the soil moisture sensor, inserted into a plant pot for monitoring.*

## Repository Structure

- `SoilSensor.py`: Initial script for reading soil moisture sensor data.
- `send_email.py`: Script for sending email notifications using SMTP.
- `SoilSensorEmail.py`: Combined script for scheduled moisture checks and email notifications.
- `SoilSensorEmailGUI.py`: Final script with Tkinter GUI integration.
- `.gitattributes`: Git configuration file.
- `plant`: Directory for additional plant-related data (if any).

## Setup Instructions

1. **Hardware Setup**:
   - Connect the soil moisture sensor (FC-28) to the Raspberry Pi:
     - VCC to 5V
     - GND to GND
     - DO (Digital Output) to GPIO 4
   - Insert the sensor probes into the plant's soil.
   - Adjust the sensor's potentiometer to set the desired moisture threshold.

2. **Software Setup**:
   - Install the required Python libraries:
     ```bash
     sudo apt update
     sudo apt install python3-rpi.gpio
     pip install tk
     ```
   - Clone the repository:
     ```bash
     git clone https://github.com/username/Project2_2025.git
     ```
   - Update the email configuration in `SoilSensorEmailGUI.py` with your SMTP server details, sender email, app password, and recipient email.

3. **Running the Program**:
   - Execute the GUI script in a Python environment:
     ```bash
     python3 SoilSensorEmailGUI.py
     ```

## Usage

- Launch the program to start monitoring.
- The GUI will display the current soil moisture status and allow you to:
  - Manually check moisture levels.
  - Add or remove scheduled check times.
  - Run diagnostics to test the system.
- Email notifications will be sent automatically at scheduled times if the soil is dry.

## Development Process

This project was developed using the Scrum framework with a single two-week sprint. Key tasks included:
- Planning and documenting user stories.
- Implementing sensor reading and email functionality.
- Developing and integrating the Tkinter GUI.
- Testing and committing changes using Git.

For more details, refer to the project report and video presentation (link to be provided in the final submission).

## Author

- **Name**: Ziheng Wang
- **Student ID**: 202283890020
- **Course & Year**: Project Semester 3 2025
- **Date**: 20/04/25
