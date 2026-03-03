# CCJS Validator Tool

## Project Overview

An AI-native Python tool that validates CCJS (Canadian Centre for Justice and Community Safety Statistics) data submissions against the UCR (Uniform Crime Reporting) Manual. The tool extracts text from the UCR Manual PDF and passes it directly to Claude to validate General Occurrence (GO) records — producing JSON and PDF reports with full UCR section traceability.

**Key design principle**: No vector DB, no embeddings, no chunking strategy. The LLM receives the full extracted UCR manual text alongside each CCJS record in a single prompt and reasons over both to identify violations.

### Pipeline

```
UCR PDF (PyMuPDF text extraction) → CCJS record data → Claude API prompt → JSON + PDF reports
```

## Domain Context

### What is CCJS?

CCJS is the Canadian crime statistics reporting system managed by the Canadian Centre for Justice and Community Safety Statistics (CCJCSS), a division of Statistics Canada. Police services submit crime data following strict rules defined in the UCR Manual.

### What is the UCR Manual?

The **Uniform Crime Reporting Survey Manual** (currently `2025_UCR_Manual.pdf`, 324 pages) defines:
- All valid offence codes (UCR codes like 1330 = Sexual Assault, 1480 = Other Assaults, 3430 = Disturb the Peace)
- Mandatory and conditional fields for each record type
- Business rules governing relationships between fields (e.g., accused status requires charge date)
- Clearance status rules, weapon type requirements, victim requirements, etc.
- Valid code tables for location codes, weapon types, vehicle types, etc.

### What is a General Occurrence (GO)?

A GO is a police incident report containing:
- **GO record**: Metadata about the incident (RIN, jurisdiction, dates, offence codes, location, weapon info, clearance status, etc.)
- **Persons**: Suspects, victims, witnesses, accused — each with demographic data, roles, and optional charges
- **Vehicles**: Involved vehicles with licence plates, VINs, makes/models
- **Businesses**: Involved business entities with optional charges

### CCJS Validation

Validation checks each GO record against UCR rules and produces errors with:
- **CCJS error code** (e.g., 5.20, 35.00, 47.10) — maps to a specific UCR rule
- **Error message** — what's wrong (e.g., "CHARGE DATE - mandatory")
- **Correction message** — how to fix it
- **Field location** — which entity and field has the issue
- **Severity** — error vs. warning (error codes like 76.16 are warnings)

## Architecture

### Target Project Structure

```
ccjs-validator/
├── CLAUDE.md                      This file
├── main.py                        CLI entry point (Typer)
├── requirements.txt               Python dependencies
├── .env.example                   Environment variable template
├── .gitignore
├── 2025_UCR_Manual.pdf            UCR Manual (324 pages, ~2.4MB)
├── extraction/
│   ├── __init__.py
│   └── pdf_extractor.py           PyMuPDF text extraction + cleaning
├── parsing/
│   ├── __init__.py
│   └── ccjs_parser.py             JSON/CSV input parser
├── validation/
│   ├── __init__.py
│   ├── engine.py                  Per-record LLM validation loop
│   ├── llm_client.py              Claude API wrapper
│   ├── prompts.py                 Prompt templates
│   └── models.py                  Pydantic models (all data models)
├── reporting/
│   ├── __init__.py
│   ├── json_reporter.py           JSON report generation
│   └── pdf_reporter.py            PDF report generation (ReportLab)
├── test_data/                     Reference test data (input GO + expected output)
│   ├── go-2024-50.json
│   ├── go-2024-50-ccjs-output.json
│   ├── go-2025-30.json
│   ├── go-2025-30-ccjs-output.json
│   ├── go-2025-4419.json
│   └── go-2025-4419-ccjs-output.json
├── outputs/                       Generated reports (gitignored)
└── tests/
    ├── __init__.py
    ├── test_extractor.py
    ├── test_parser.py
    ├── test_validation_engine.py
    └── test_reporters.py
```

### Module Responsibilities

| Module | Purpose |
|---|---|
| `extraction/pdf_extractor.py` | Open UCR PDF with PyMuPDF (`fitz`), extract full text or page ranges, clean whitespace/artifacts |
| `parsing/ccjs_parser.py` | Read GO JSON files, validate structure, parse into Pydantic models |
| `validation/engine.py` | Iterate over records, build prompts with UCR text + record data, call Claude, parse responses |
| `validation/llm_client.py` | Thin wrapper around `anthropic.Anthropic()` — handles API calls, retries, token counting |
| `validation/prompts.py` | Prompt templates for validation. Include UCR text, record JSON, output schema instructions |
| `validation/models.py` | All Pydantic models: `GORecord`, `Person`, `Vehicle`, `Business`, `Violation`, `ValidationResult`, `ValidationReport` |
| `reporting/json_reporter.py` | Compile validation results into the JSON output format matching `*-ccjs-output.json` structure |
| `reporting/pdf_reporter.py` | Generate PDF report with error tables, UCR section references, correction instructions |
| `main.py` | Typer CLI: `validate` command with `--manual`, `--data`, `--format`, `--output-dir` options |

## Data Models

### Input: GO Record (`go-*.json`)

```python
class GORecord(BaseModel):
    rin: int                              # Record Identification Number
    primary_key: str | None = None        # e.g., "202450"
    jurisdiction: str | None = None       # 4-char jurisdiction code
    ccjs_flag: int                        # 1 = CCJS reportable
    occ_date: str                         # Occurrence date (YYYY-MM-DD)
    occ_time: int                         # Occurrence time (HHMM)
    to_occ_date: str | None = None        # End date for range
    to_occ_time: int | None = None
    rep_date: str                         # Report date
    rep_time: int                         # Report time
    founded: str                          # Clearance status: X, N, C, W, etc.
    rucr: str                             # Primary UCR offence code (e.g., "3430")
    rext: str                             # Extension code
    rucr1_comp: str                       # A=Attempted, C=Completed
    rucr2: str | None = None              # Secondary offence (up to 4)
    # ... rucr3, rucr4 with ext and comp
    location_code: int | None = None
    occupancy_code: int | None = None
    vehicle_type: int | None = None
    vehicle_target: int | None = None
    weapon_type: int | None = None
    weapon_status: int | None = None
    object_of_theft1: int | None = None   # Up to 5
    fraud_type: int | None = None
    violation_count: int | None = None
    ocsg_involv: str | None = None        # Organized crime
    ocsg_type: str | None = None
    cyber_crime_ind: str | None = None
    cyber_crime_type: str | None = None
    cyber_crime_class: str | None = None
    hate_crime_ind: str | None = None
    family_violence: str | None = None    # "N" or "Y"
    drug_alcohol: str | None = None
    gang_involvement: str | None = None
    gang_type: str | None = None
    firearms_stolen: str | None = None
    firearm_discharged: str | None = None
    clearance_info: str                   # "N", "C", "W", etc.
    clearance_date: str | None = None
    details: dict = {}                    # hate_crimes, stolen_vehicles sub-objects
    x_coordinate: float | None = None
    y_coordinate: float | None = None

class Person(BaseModel):
    type: str = "PER"
    pin: int                              # Person Identification Number
    type_of_pin: str                      # "I" = Individual
    role: int                             # 2=Accused, 14=Witness, 20=Complainant, 21=Victim, 80=Other
    role_number: int
    surname: str
    g1: str                               # Given name 1
    g2: str | None = None                 # Given name 2
    sex: str                              # "M", "F"
    dob: str | None = None                # YYYY-MM-DD
    yob: int | None = None
    race: str | None = None
    accused_status: int | None = None     # 1=Charged, etc.
    charge_date: str | None = None
    charges: list = []                    # List of charge objects

class Vehicle(BaseModel):
    type: str = "VEH"
    zin: int                              # Vehicle ID
    role: int                             # 8=Involved
    veh_number: int
    licence_num: str | None = None
    poi: str | None = None                # Province ("ONT")
    vin: str | None = None
    veh_type: str | None = None
    veh_year: int | None = None
    veh_make: str | None = None
    veh_model: str | None = None

class Business(BaseModel):
    type: str = "BUS"
    bin: int                              # Business Identification Number
    busname: str
    role: int                             # 15=Involved
    role_number: int
    accused_status: int | None = None
    # Up to 4 charges with act, section, wording, count

class FullGORecord(BaseModel):
    """Top-level input structure."""
    go: GORecord
    persons: list[Person] = []
    vehicles: list[Vehicle] = []
    businesses: list[Business] = []
```

### Output: Validation Report (`*-ccjs-output.json`)

```python
class ErrorLink(BaseModel):
    link_text: str                        # "Modify the Accused", "Modify the GO", "Add (Person) Victim"
    link: str                             # JSON string with ErrorNo, Type, EntityKey, RMSFieldId
    link_obj: dict = {}

class ValidationError(BaseModel):
    error_no: int                         # Sequential error number
    collapse_toggle: str = "in"           # UI state
    error_link_arr: list[ErrorLink]       # Navigation links to fix the error
    jurisdiction: str
    primary_key: str                      # e.g., "    20254419"
    occ_num: int                          # Occurrence number
    report_date: str
    operational_code: str                 # "B" = ...
    offence_code: str                     # UCR code
    offence_ext: str
    offence_att_comp: str                 # "C"=Completed
    ccjs_code: str                        # Error code (e.g., "5.20", "35.00")
    offence_trans: str                    # Offence translation (e.g., "DISTURB TH PEACE")
    error_in_field: str                   # Which field/entity has the error
    ccjs_error_code: float                # Numeric error code
    ccjs_error_message: str               # Short error description
    error_details: str | None = None      # Additional context
    correction_message: str               # How to fix the error

class ValidationReport(BaseModel):
    template: dict                        # Display template settings
    case_number: str                      # e.g., "2025-4419 A DEMS ONE"
    labels: dict                          # UI labels
    comments: dict                        # UI comments
    errors: list[ValidationError]
```

## Known CCJS Error Codes (from test data)

| Code | Message | Rule Summary |
|---|---|---|
| 5.20 | CHARGE DATE - mandatory | Charge date required when accused status is entered |
| 5.50 | DATE OF BIRTH or APPROXIMATE AGE - mandatory | DOB or approx age must exist on person |
| 18.10 | 1st CHARGE - required | Charge required when accused status = 1 (Charged) |
| 32.80 | CCJS STATUS - invalid | When accused has status 1, clearance must be C or W |
| 33.00 | OCCUPANCY - invalid | Occupancy must be blank for non-violent offences at certain locations |
| 35.00 | VICTIM - required | Violent (1000-series) or criminal traffic (9000-series) offences need a victim |
| 42.00 | CCJS STATUS - invalid | CCJS status cannot be A, B, X, Y, or Z when accused entities are present |
| 47.10 | WEAPON TYPE - invalid | Weapon type cannot be blank or 14 (No weapon) for certain offences |
| 47.20 | WEAPON TYPE - mandatory | Weapon type must be entered for certain offences |
| 76.16 | WARNING - Hate crime is blank | Hate crime detail page exists but hate crime field is blank/No (warning, not error) |

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| PDF Extraction | PyMuPDF (`fitz`) |
| LLM | Anthropic Claude API (`anthropic` package) |
| Data Models | Pydantic v2 |
| CLI | Typer |
| PDF Reports | ReportLab |
| Config | python-dotenv |
| Testing | pytest |

## Environment Variables

```
ANTHROPIC_API_KEY=sk-ant-...      # Required
MODEL=claude-sonnet-4-20250514    # Default model (override as needed)
OUTPUT_DIR=outputs                # Report output directory
```

## Development Conventions

### Python Style
- Python 3.11+ with type hints throughout
- Pydantic v2 models for all data structures (use `model_validator`, `field_validator`)
- Use `from __future__ import annotations` for forward references
- Snake_case for functions/variables, PascalCase for classes
- Keep modules focused — one responsibility per file
- Prefer explicit imports over star imports

### Error Handling
- Raise specific exceptions, not generic `Exception`
- Log LLM API errors with full context (model, token count, prompt excerpt)
- Validation errors are data (captured in models), not Python exceptions

### Testing
- Run tests: `pytest tests/`
- Test data lives in `test_data/` — input GO files paired with expected output files
- Test naming: `test_<module>_<behavior>.py`
- Use the 3 existing test cases as golden reference for validation accuracy:
  - `go-2025-4419.json` → 5 errors (5.20, 5.50, 18.10, 42.00, 32.80)
  - `go-2024-50.json` → 3 errors (47.20, 76.16, 35.00)
  - `go-2025-30.json` → 3 errors (47.10, 35.00, 33.00)

### LLM Usage
- Use the `anthropic` Python SDK (not raw HTTP)
- Claude's 200k context window handles the full UCR manual (~324 pages)
- If the manual exceeds the limit, trim non-rule sections first
- Prompt structure: system message with UCR text + user message with GO record JSON
- Response must be structured JSON matching the output schema
- Always include `ucr_section` traceability in validation results

### CLI
- Entry point: `python main.py validate`
- Required args: `--manual` (path to UCR PDF), `--data` (path to GO JSON)
- Optional: `--format pdf,json` (default: both), `--output-dir` (default: `outputs/`)

### Git
- Do not commit `.env`, `outputs/`, or `__pycache__/`
- Do not commit the UCR manual PDF to remote (it's large and potentially sensitive)
- Commit messages: imperative mood, lowercase, concise

## UCR Manual Reference

- File: `2025_UCR_Manual.pdf` (324 pages, ~2.4MB)
- Published: December 2025 by CCJCSS (Statistics Canada)
- Contains: offence code tables, field definitions, validation rules, code tables for all categorical fields
- Key sections: Section 1 (Changes), Section 2 (Introduction), subsequent sections define fields, codes, and rules
- The full text is extracted via PyMuPDF and passed to Claude as context for validation

## Test Data Reference

Three test cases exist in `test_data/`:

### GO 2025-4419 (Disturb the Peace)
- **Input**: `go-2025-4419.json` — 2 persons (victim role 21, accused role 2 with status 1 but no charges/charge date/DOB), 2 vehicles, 1 business. Founded=X.
- **Expected**: 5 errors — missing charge date (5.20), missing DOB (5.50), missing charge (18.10), invalid CCJS status with accused present (42.00), clearance must be C/W when accused status=1 (32.80)

### GO 2024-50 (Sexual Assault)
- **Input**: `go-2024-50.json` — 1 person (complainant role 20), no vehicles, no businesses. Founded=X, offence 1330.
- **Expected**: 3 errors — weapon type mandatory for offence (47.20), hate crime blank warning (76.16), victim required for violent offence (35.00)

### GO 2025-30 (Other Assaults)
- **Input**: `go-2025-30.json` — 2 persons (witness role 14, other role 80), no vehicles, no businesses. Founded=X, offence 1480, occupancy_code=9.
- **Expected**: 3 errors — weapon type invalid/blank for offence (47.10), victim required for violent offence (35.00), occupancy invalid for non-violent at location (33.00)
