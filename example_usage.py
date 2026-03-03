"""
Example usage of the CCJS parser to demonstrate accessing structured data.
"""

from parser import CCJSParser, CCJSReport
import json


def demonstrate_parser_usage():
    """Demonstrate various ways to use the CCJS parser."""
    
    print("=== CCJS Parser Usage Examples ===\n")
    
    # Example 1: Parse from file
    print("1. Parsing from file:")
    parser = CCJSParser()
    report = parser.parse_file("test_data/go-2025-4419.json")
    
    # Access structured data
    print(f"   RIN: {report.go.rin}")
    print(f"   Jurisdiction: '{report.go.jurisdiction.strip()}'")
    print(f"   CCJS Flag: {report.go.ccjs_flag}")
    print(f"   Family Violence: {report.go.family_violence}")
    
    # Example 2: Working with persons
    print(f"\n2. Person details ({len(report.persons)} persons):")
    for person in report.persons:
        print(f"   PIN: {person.pin}")
        print(f"   Name: {person.surname}, {person.g1}")
        print(f"   Sex: {person.sex}")
        print(f"   DOB: {person.dob}")
        print(f"   Role: {person.role}")
        if person.accused_status:
            print(f"   Accused Status: {person.accused_status}")
        print()
    
    # Example 3: Working with vehicles
    print(f"3. Vehicle details ({len(report.vehicles)} vehicles):")
    for i, vehicle in enumerate(report.vehicles, 1):
        print(f"   Vehicle {i}:")
        print(f"     ZIN: {vehicle.zin}")
        print(f"     License: {vehicle.licence_num}")
        print(f"     Province: {vehicle.poi}")
        print(f"     Make/Model: {vehicle.veh_make} {vehicle.veh_model}")
        print(f"     Year: {vehicle.veh_year}")
        print(f"     Color: {vehicle.veh_color}")
        print()
    
    # Example 4: Working with businesses
    print(f"4. Business details ({len(report.businesses)} businesses):")
    for business in report.businesses:
        print(f"   BIN: {business.bin}")
        print(f"   Name: {business.busname}")
        print(f"   Role: {business.role}")
        print()
    
    # Example 5: Data validation and type checking
    print("5. Data validation examples:")
    print(f"   Is GO founded? {report.go.founded == 'X'}")
    print(f"   Has family violence? {report.go.family_violence == 'Y'}")
    print(f"   Number of male persons: {sum(1 for p in report.persons if p.sex == 'M')}")
    print(f"   Vehicles with VIN: {sum(1 for v in report.vehicles if v.vin)}")
    
    # Example 6: Convert back to dict/JSON
    print(f"\n6. Data serialization:")
    print("   Converting back to dictionary...")
    
    # You can access the original data structure if needed
    # Note: dataclasses can be converted using asdict() from dataclasses module
    from dataclasses import asdict
    report_dict = asdict(report)
    
    print(f"   Dictionary keys: {list(report_dict.keys())}")
    print(f"   GO fields count: {len(report_dict['go'])}")
    
    return report


def validate_data_types(report: CCJSReport):
    """Demonstrate type validation and error handling."""
    
    print("\n=== Data Type Validation ===")
    
    # Validate required fields
    assert isinstance(report.go.rin, int), "RIN should be an integer"
    assert isinstance(report.go.ccjs_flag, int), "CCJS flag should be an integer"
    
    # Validate optional fields
    if report.go.occ_date:
        assert isinstance(report.go.occ_date, str), "Occurrence date should be a string"
    
    # Validate lists
    assert isinstance(report.persons, list), "Persons should be a list"
    assert isinstance(report.vehicles, list), "Vehicles should be a list"
    assert isinstance(report.businesses, list), "Businesses should be a list"
    
    print("? All data types validated successfully!")


def search_example(report: CCJSReport):
    """Demonstrate searching and filtering the parsed data."""
    
    print("\n=== Search and Filter Examples ===")
    
    # Find persons by role
    suspects = [p for p in report.persons if p.role == 2]  # Role 2 might be suspect
    victims = [p for p in report.persons if p.role == 21]  # Role 21 might be victim
    
    print(f"Suspects found: {len(suspects)}")
    print(f"Victims found: {len(victims)}")
    
    # Find vehicles by type
    passenger_vehicles = [v for v in report.vehicles if v.veh_type == "1"]
    print(f"Passenger vehicles: {len(passenger_vehicles)}")
    
    # Find if any weapons were involved
    weapons_involved = any(w for p in report.persons if p.weapon for w in [p.weapon] if w)
    print(f"Weapons involved: {weapons_involved}")
    
    return suspects, victims


if __name__ == "__main__":
    # Run all examples
    report = demonstrate_parser_usage()
    validate_data_types(report)
    search_example(report)
    
    print(f"\n=== Summary ===")
    print(f"Successfully parsed CCJS report RIN {report.go.rin}")
    print(f"Report contains {len(report.persons)} persons, {len(report.vehicles)} vehicles, {len(report.businesses)} businesses")