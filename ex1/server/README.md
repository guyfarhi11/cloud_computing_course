# Parking Lot Application

## Project Overview
This project is a simple parking lot management system built using Flask and SQLAlchemy. 
It allows vehicles to enter and exit a parking lot, and calculates the parking charges based on the duration of stay.

## Folder Structure

- deploy.sh
- requirements.txt
- app.py


## Files

### deploy.sh
This shell script sets up the environment by updating the system packages, installing necessary packages, 
cloning the repository, creating a virtual environment, and installing required Python packages.

### requirements.txt
This file lists the required Python packages for the project

### app.py
This is the main Flask application file. 
It defines the routes for vehicle entry and exit, and manages the SQLite database using SQLAlchemy.

## Usage
- To enter a vehicle into the parking lot, send a POST request to `/entry` with the `plate` and `parkingLot` parameters.
- To exit a vehicle from the parking lot, send a POST request to `/exit` with the `ticketId` parameter.
