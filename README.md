# CCJS Validator

A Python parser for Canadian Centre for Justice Statistics (CCJS) data files.

## Overview

This project provides a robust parser for CCJS JSON files, converting them into well-defined Python data structures using dataclasses. It's designed to handle General Occurrence (GO) reports with associated persons, vehicles, and businesses.

## Features

- **Type-safe parsing**: Uses Python dataclasses for structured data
- **Comprehensive coverage**: Handles all fields from CCJS GO reports
- **Flexible input**: Parse from files, dictionaries, or JSON strings
- **Validation**: Built-in data type validation and error handling
- **Easy to use**: Simple API with clear examples

## Quick Start

### 1. Setup (using uv - recommended)

```bash
# Create virtual environment
uv venv

# Activate environment
.venv\Scripts\Activate.ps1

# Install optional dependencies (if needed)
uv pip install -r requirements.txt
```

### 2. Basic Usage

```python
from parser import CCJSParser

# Parse a CCJS file
parser = CCJSParser()
report = parser.parse_file("test_data/go-2025-4419.json")

# Access structured data
print(f"RIN: {report.go.rin}")
print(f"Occurrence Date: {report.go.occ_date}")
print(f"Number of persons: {len(report.persons)}")

# Work with persons
for person in report.persons:
    print(f"Name: {person.surname}, {person.g1}")
    print(f"Role: {person.role}")
```

### 3. Run Examples

```bash
# Run the basic parser demo
python parser.py

# Run comprehensive usage examples
python example_usage.py
```

## Data Structure

### Main Classes

- **`CCJSReport`**: Top-level container for all data
- **`GeneralOccurrence`**: Main incident details (GO record)
- **`Person`**: Individual person records  
- **`Vehicle`**: Vehicle records
- **`Business`**: Business entity records

### Key Fields

**GeneralOccurrence (GO)**:
- `rin`: Record Identification Number
- `occ_date`/`occ_time`: Occurrence date/time
- `rep_date`/`rep_time`: Report date/time
- `location_code`: Location where incident occurred
- `founded`: Whether the occurrence was founded

**Person**:
- `pin`: Person Identification Number
- `role`: Person's role in the incident
- `surname`/`g1`: Name fields
- `sex`, `dob`, `yob`: Demographics

**Vehicle**:
- `zin`: Zone Identification Number  
- `licence_num`: License plate number
- `vin`: Vehicle Identification Number
- `veh_make`/`veh_model`: Make and model

## Error Handling

The parser includes robust error handling for:
- Missing files (`FileNotFoundError`)
- Invalid JSON (`JSONDecodeError`) 
- Missing required fields (`KeyError`)
- Type validation errors

## Testing Your Data

To test with your own CCJS files:

```python
# Test with your file
try:
    report = CCJSParser.parse_file("path/to/your/file.json")
    print(f"Successfully parsed RIN: {report.go.rin}")
except Exception as e:
    print(f"Error: {e}")
```

## File Structure

```
ccjs-validator/
??? parser.py           # Main parser classes and functions
??? example_usage.py    # Comprehensive usage examples  
??? requirements.txt    # Optional dependencies
??? test_data/         # Sample CCJS files
?   ??? go-2025-4419.json
??? README.md          # This file
```

## Dependencies

The core parser uses **only Python standard library** - no external dependencies required!

Optional dependencies in `requirements.txt` are for enhanced features:
- `pydantic`: Enhanced data validation
- `pytest`: Testing framework  
- `mypy`: Type checking

## License

This project is designed for parsing CCJS data files in compliance with Canadian justice statistics requirements.