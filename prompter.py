"""
CCJS MSV Validation Prompter - Generates prompts for Most Serious Violation validation.

This module creates structured prompts for validating Most Serious Violation (MSV) data 
in CCJS ingestion pipelines, focusing on incident date, completion status, weapon compatibility,
victim requirements, age restrictions, relationships, and injury consistency.
"""

from typing import List, Dict, Any, Optional
from parser import CCJSReport, CCJSParser


class CCJSMSVPrompter:
    """Generates MSV validation prompts for CCJS data processing pipelines."""
    
    def __init__(self, report: Optional[CCJSReport] = None):
        """
        Initialize the MSV prompter with optional CCJS report data.
        
        Args:
            report: Optional CCJSReport object to generate context-aware prompts
        """
        self.report = report
    
    def generate_msv_validation_prompts(self) -> List[str]:
        """
        Generate Most Serious Violation (MSV) validation prompts for the ingestion pipeline.
        
        Returns:
            List of MSV-specific validation prompt strings
        """
        prompts = [
            "Check if the 'to incident date' is appropriate and valid for the Most Serious Violation (MSV). Verify that the to_occ_date field aligns with MSV classification requirements and reporting standards.",
            
            "Determine if the Most Serious Violation (MSV) needs to be marked as completed or if completion status is not applicable for this record. Evaluate based on incident characteristics and reporting requirements.",
            
            "Validate compatibility between Most Serious Weapon present, weapon status, and Most Serious Violation code. Ensure these three fields are logically consistent and properly aligned with each other.",
            
            "Check if a victim record is required for the Most Serious Violation (MSV). Verify that victim presence/absence aligns with the nature of the MSV and CCJS reporting requirements.",
            
            "Validate age restrictions for victims in relation to the Most Serious Violation (MSV). Check if victim age meets or violates any age-based requirements for the specific MSV classification.",
            
            "Examine relationship value restrictions for the Most Serious Violation (MSV). Verify that victim-offender relationship codes are appropriate and allowed for the specific MSV type.",
            
            "Check compatibility between level of injury, weapon causing injury, and the Most Serious Violation (MSV). Ensure injury details are consistent with the MSV classification and weapon involvement."
        ]
        
        if self.report:
            # Add context-aware prompts based on actual data
            msv_context = []
            
            # Check UCR codes (likely representing MSV)
            if self.report.go.rucr:
                msv_context.append(f"MSV code {self.report.go.rucr}")
                if self.report.go.rucr1_comp:
                    msv_context.append(f"completion status: {self.report.go.rucr1_comp}")
            
            # Check weapon information
            weapon_info = []
            if self.report.go.weapon_type:
                weapon_info.append(f"weapon type: {self.report.go.weapon_type}")
            if self.report.go.weapon_status:
                weapon_info.append(f"weapon status: {self.report.go.weapon_status}")
            
            # Check victim information
            victims = [p for p in self.report.persons if p.role in [21, 22, 23]]  # Common victim role codes
            victim_info = []
            if victims:
                victim_info.append(f"{len(victims)} victim record(s)")
                # Check for age and relationship data
                victims_with_age = [v for v in victims if v.dob or v.yob]
                if victims_with_age:
                    victim_info.append(f"{len(victims_with_age)} with age information")
                victims_with_relation = [v for v in victims if v.relation]
                if victims_with_relation:
                    victim_info.append(f"{len(victims_with_relation)} with relationship data")
            
            # Check injury information
            injured_persons = [p for p in self.report.persons if p.level_of_injury]
            injury_info = []
            if injured_persons:
                injury_info.append(f"{len(injured_persons)} person(s) with injury levels")
                weapon_injuries = [p for p in injured_persons if p.weapon]
                if weapon_injuries:
                    injury_info.append(f"{len(weapon_injuries)} with weapon causing injury")
            
            # Generate context-specific prompts
            context_summary = f"RIN {self.report.go.rin}: {', '.join(msv_context) if msv_context else 'MSV data needs validation'}"
            
            prompts.extend([
                f"Validate MSV data for {context_summary}. Check to incident date {self.report.go.to_occ_date} against MSV requirements.",
                
                f"Review MSV completion requirements for this record. Weapon information: {', '.join(weapon_info) if weapon_info else 'no weapon data'}.",
                
                f"Cross-reference MSV with victim requirements. Victim status: {', '.join(victim_info) if victim_info else 'no victim records identified'}.",
                
                f"Validate MSV injury consistency. Injury details: {', '.join(injury_info) if injury_info else 'no injury data recorded'}."
            ])
        
        return prompts
    
    def generate_msv_completion_check_prompts(self) -> List[str]:
        """
        Generate specific prompts for MSV completion status validation.
        
        Returns:
            List of MSV completion check prompt strings
        """
        prompts = [
            "Evaluate if the Most Serious Violation (MSV) requires completion marking based on incident resolution status and investigative outcomes.",
            
            "Check MSV completion requirements against case clearance information. Determine if completion status affects statistical reporting requirements.",
            
            "Assess whether MSV completion is mandatory, optional, or not applicable based on the specific violation type and jurisdictional requirements."
        ]
        
        if self.report:
            completion_status = self.report.go.rucr1_comp if self.report.go.rucr1_comp else "unknown"
            clearance_info = self.report.go.clearance_info if self.report.go.clearance_info else "not specified"
            
            prompts.extend([
                f"Review MSV completion for RIN {self.report.go.rin}. Current completion status: {completion_status}, clearance info: {clearance_info}.",
                
                "Determine if completion status changes are required based on current case status and reporting requirements."
            ])
        
        return prompts
    
    def generate_msv_compatibility_check_prompts(self) -> List[str]:
        """
        Generate prompts for checking MSV field compatibility and consistency.
        
        Returns:
            List of MSV compatibility check prompt strings
        """
        prompts = [
            "Verify logical consistency between Most Serious Weapon, weapon status, and MSV code. Ensure weapon presence aligns with violation type requirements.",
            
            "Check if weapon status indicators are compatible with the Most Serious Violation classification and incident characteristics.",
            
            "Validate that Most Serious Weapon designation matches the severity and nature of the MSV code classification.",
            
            "Cross-reference weapon availability (status), weapon type, and MSV to ensure they represent a coherent incident scenario."
        ]
        
        return prompts
    
    def generate_msv_victim_requirement_prompts(self) -> List[str]:
        """
        Generate prompts for MSV victim requirement validation.
        
        Returns:
            List of MSV victim requirement prompt strings
        """
        prompts = [
            "Determine if the Most Serious Violation (MSV) legally requires a victim record or if victimless classification applies.",
            
            "Validate victim record presence against MSV type requirements. Some violations mandate victim records while others may not.",
            
            "Check if MSV victim requirements are met based on violation classification and jurisdictional reporting standards."
        ]
        
        return prompts
    
    def generate_all_msv_prompts(self) -> Dict[str, List[str]]:
        """
        Generate all MSV validation prompts organized by category.
        
        Returns:
            Dictionary containing all MSV prompt categories
        """
        return {
            "msv_validation": self.generate_msv_validation_prompts(),
            "msv_completion": self.generate_msv_completion_check_prompts(),
            "msv_compatibility": self.generate_msv_compatibility_check_prompts(),
            "msv_victim_requirements": self.generate_msv_victim_requirement_prompts()
        }


def get_msv_prompts_array(ccjs_file_path: str = None) -> List[str]:
    """
    Convenience function to get MSV validation prompts array for pipeline integration.
    
    Args:
        ccjs_file_path: Optional path to CCJS file for context-aware prompts
        
    Returns:
        List[str]: Array of MSV validation prompt strings ready for pipeline
    """
    if ccjs_file_path:
        try:
            prompter = create_msv_prompter_from_file(ccjs_file_path)
        except:
            prompter = CCJSMSVPrompter()
    else:
        prompter = CCJSMSVPrompter()
    
    return prompter.generate_msv_validation_prompts()


def create_msv_prompter_from_file(file_path: str) -> CCJSMSVPrompter:
    """
    Create a CCJSMSVPrompter instance from a CCJS JSON file.
    
    Args:
        file_path: Path to the CCJS JSON file
        
    Returns:
        CCJSMSVPrompter instance with loaded data
    """
    parser = CCJSParser()
    report = parser.parse_file(file_path)
    return CCJSMSVPrompter(report)


def main():
    """Demonstrate MSV prompter functionality."""
    print("=== CCJS MSV Validation Prompter ===\n")
    
    try:
        prompter = create_msv_prompter_from_file("test_data/go-2025-4419.json")
        print(f"? Loaded CCJS report RIN: {prompter.report.go.rin}")
    except:
        prompter = CCJSMSVPrompter()
        print("? Using MSV prompter without specific data")
    
    print("\n--- MSV VALIDATION PROMPTS ---")
    msv_prompts = prompter.generate_msv_validation_prompts()
    for i, prompt in enumerate(msv_prompts, 1):
        print(f"{i}. {prompt}")
    
    print(f"\nTotal MSV validation prompts: {len(msv_prompts)}")
    
    print(f"\n--- ALL MSV CATEGORIES ---")
    all_prompts = prompter.generate_all_msv_prompts()
    total = 0
    for category, prompts in all_prompts.items():
        print(f"{category.replace('_', ' ').title()}: {len(prompts)} prompts")
        total += len(prompts)
    
    print(f"\nTotal MSV prompts available: {total}")
    print("Ready for MSV validation pipeline! ??")


if __name__ == "__main__":
    main()
