"""
CCJS Data Parser - Parses CCJS JSON files into well-defined data structures.

This module provides dataclasses and parsing functions for CCJS (Canadian Centre for Justice Statistics)
data files, specifically for General Occurrence (GO) reports.
"""

import json
from dataclasses import dataclass, field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime, date, time


@dataclass
class Details:
    """Details section containing hate crimes and stolen vehicles."""
    hate_crimes: List[Dict[str, Any]] = field(default_factory=list)
    stolen_vehicles: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GeneralOccurrence:
    """General Occurrence (GO) main record containing incident details."""
    rin: int
    jurisdiction: str
    ccjs_flag: int
    occ_date: Optional[str]
    occ_time: Optional[int]
    to_occ_date: Optional[str]
    to_occ_time: Optional[int]
    rep_date: Optional[str]
    rep_time: Optional[int]
    founded: Optional[str]
    rucr: Optional[str]
    rext: Optional[str]
    rucr1_comp: Optional[str]
    rucr2: Optional[str]
    rext2: Optional[str]
    rucr2_comp: Optional[str]
    rucr3: Optional[str]
    rext3: Optional[str]
    rucr3_comp: Optional[str]
    rucr4: Optional[str]
    rext4: Optional[str]
    rucr4_comp: Optional[str]
    location_code: Optional[int]
    occupancy_code: Optional[str]
    vehicle_type: Optional[str]
    vehicle_target: Optional[str]
    weapon_type: Optional[str]
    weapon_status: Optional[str]
    object_of_theft1: Optional[str]
    object_of_theft2: Optional[str]
    object_of_theft3: Optional[str]
    object_of_theft4: Optional[str]
    object_of_theft5: Optional[str]
    fraud_type: Optional[str]
    violation_count: Optional[int]
    ocsg_involv: Optional[str]
    ocsg_type: Optional[str]
    cyber_crime_ind: Optional[str]
    cyber_crime_type: Optional[str]
    cyber_crime_class: Optional[str]
    hate_crime_ind: Optional[str]
    family_violence: Optional[str]
    drug_alcohol: Optional[str]
    gang_involvement: Optional[str]
    gang_type: Optional[str]
    firearms_stolen: Optional[str]
    firearm_discharged: Optional[str]
    clearance_info: Optional[str]
    clearance_date: Optional[str]
    details: Details

    def __post_init__(self):
        """Post-initialization processing to convert raw data."""
        # Convert details dict to Details object if needed
        if isinstance(self.details, dict):
            self.details = Details(**self.details)


@dataclass
class Charge:
    """Individual charge information."""
    act: Optional[str] = None
    section: Optional[str] = None
    wording: Optional[str] = None
    count: Optional[int] = None


@dataclass
class Person:
    """Person record containing individual details."""
    type: str
    pin: int
    type_of_pin: Optional[str]
    role: Optional[int]
    role_number: Optional[int]
    surname: Optional[str]
    g1: Optional[str]  # Given name 1
    sex: Optional[str]
    dob: Optional[str]  # Date of birth
    yob: Optional[int]  # Year of birth
    race: Optional[str]
    resident_status: Optional[str]
    ucr: Optional[str]
    ext: Optional[str]
    level_of_injury: Optional[str]
    weapon: Optional[str]
    relation: Optional[str]
    peace_officer: Optional[str]
    accused_role: Optional[str]
    accused_number: Optional[int]
    accused_status: Optional[int]
    charge_date: Optional[str]
    laid_by_victim: Optional[str]
    charges: List[Charge] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing to convert raw data."""
        # Convert charges list if needed
        if self.charges and isinstance(self.charges[0], dict):
            self.charges = [Charge(**charge) for charge in self.charges]


@dataclass
class Vehicle:
    """Vehicle record containing vehicle details."""
    type: str
    zin: int
    role: Optional[int]
    veh_number: Optional[int]
    licence_num: Optional[str]
    poi: Optional[str]  # Province of issue
    year_of_issue: Optional[int]
    plate_type: Optional[str]
    vin: Optional[str]
    veh_type: Optional[str]
    veh_year: Optional[int]
    veh_make: Optional[str]
    veh_model: Optional[str]
    veh_style: Optional[str]
    veh_color: Optional[str]


@dataclass
class Business:
    """Business record containing business entity details."""
    type: str
    bin: int
    busname: Optional[str]
    role: Optional[int]
    role_number: Optional[int]
    accused_status: Optional[int]
    charge_date: Optional[str]
    charge_1_act: Optional[str]
    charge_1_section: Optional[str]
    charge_1_wording: Optional[str]
    charge_1_count: Optional[int]
    charge_2_act: Optional[str]
    charge_2_section: Optional[str]
    charge_2_wording: Optional[str]
    charge_2_count: Optional[int]
    charge_3_act: Optional[str]
    charge_3_section: Optional[str]
    charge_3_wording: Optional[str]
    charge_3_count: Optional[int]
    charge_4_act: Optional[str]
    charge_4_section: Optional[str]
    charge_4_wording: Optional[str]
    charge_4_count: Optional[int]


@dataclass
class CCJSReport:
    """Main CCJS report containing all related records."""
    go: GeneralOccurrence
    persons: List[Person] = field(default_factory=list)
    vehicles: List[Vehicle] = field(default_factory=list)
    businesses: List[Business] = field(default_factory=list)

    def __post_init__(self):
        """Post-initialization processing to convert raw data."""
        # Convert GO dict to GeneralOccurrence object if needed
        if isinstance(self.go, dict):
            self.go = GeneralOccurrence(**self.go)
        
        # Convert persons list
        if self.persons and isinstance(self.persons[0], dict):
            self.persons = [Person(**person) for person in self.persons]
        
        # Convert vehicles list
        if self.vehicles and isinstance(self.vehicles[0], dict):
            self.vehicles = [Vehicle(**vehicle) for vehicle in self.vehicles]
        
        # Convert businesses list
        if self.businesses and isinstance(self.businesses[0], dict):
            self.businesses = [Business(**business) for business in self.businesses]


class CCJSParser:
    """Parser class for CCJS JSON files."""
    
    @staticmethod
    def parse_file(file_path: str) -> CCJSReport:
        """
        Parse a CCJS JSON file and return a structured CCJSReport object.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            CCJSReport: Parsed and structured data
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file contains invalid JSON
            KeyError: If required fields are missing
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            return CCJSParser.parse_dict(data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"CCJS file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON in file {file_path}: {e}")
    
    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> CCJSReport:
        """
        Parse a dictionary containing CCJS data.
        
        Args:
            data: Dictionary with CCJS data
            
        Returns:
            CCJSReport: Parsed and structured data
        """
        return CCJSReport(**data)
    
    @staticmethod
    def parse_json_string(json_string: str) -> CCJSReport:
        """
        Parse a JSON string containing CCJS data.
        
        Args:
            json_string: JSON string with CCJS data
            
        Returns:
            CCJSReport: Parsed and structured data
            
        Raises:
            json.JSONDecodeError: If the string contains invalid JSON
        """
        try:
            data = json.loads(json_string)
            return CCJSParser.parse_dict(data)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON string: {e}")


def main():
    """Example usage of the CCJS parser."""
    # Parse the test file
    parser = CCJSParser()
    
    try:
        # Parse the example file
        report = parser.parse_file("test_data/go-2025-4419.json")
        
        # Display parsed information
        print("=== CCJS Report Parser ===")
        print(f"RIN: {report.go.rin}")
        print(f"Occurrence Date: {report.go.occ_date}")
        print(f"Report Date: {report.go.rep_date}")
        print(f"Location Code: {report.go.location_code}")
        print(f"Founded: {report.go.founded}")
        
        print(f"\nPersons: {len(report.persons)}")
        for i, person in enumerate(report.persons, 1):
            print(f"  {i}. {person.surname}, {person.g1} (Role: {person.role})")
        
        print(f"\nVehicles: {len(report.vehicles)}")
        for i, vehicle in enumerate(report.vehicles, 1):
            print(f"  {i}. {vehicle.veh_make} {vehicle.veh_model} ({vehicle.licence_num})")
        
        print(f"\nBusinesses: {len(report.businesses)}")
        for i, business in enumerate(report.businesses, 1):
            print(f"  {i}. {business.busname} (Role: {business.role})")
            
    except Exception as e:
        print(f"Error parsing CCJS file: {e}")


if __name__ == "__main__":
    main()
