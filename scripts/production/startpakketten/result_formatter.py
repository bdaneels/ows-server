"""
Result formatting utilities to standardize all output data structures.
"""
from typing import Dict, Any, List


def format_warning(student_data: Dict[str, Any], warning_type: str) -> Dict[str, Any]:
    """
    Format a single student warning into the standardized format.
    
    Args:
        student_data: Dictionary containing student data from various sources
        warning_type: Type of warning (FAIL_adviesrapport, SP_mismatch_predelib, SP_mismatch_dashboard)
    
    Returns:
        Standardized warning dictionary
    """
    # Handle different key formats from different sources
    student_id = str(student_data.get('ID', ''))
    
    # Handle 'Name' (from compare_sp) vs separate 'Voornaam'/'Achternaam'
    if 'Name' in student_data:
        # From compare_sp.py - Name is "Voornaam Achternaam"
        name_parts = student_data['Name'].split(' ', 1)
        voornaam = name_parts[0] if name_parts else ''
        achternaam = name_parts[1] if len(name_parts) > 1 else ''
    else:
        voornaam = student_data.get('Voornaam', '')
        achternaam = student_data.get('Achternaam', '')
    
    email = student_data.get('E-mail', student_data.get('email', ''))
    
    # Build warning message based on type
    waarschuwing = _build_warning_message(student_data, warning_type)
    
    return {
        "student_id": student_id,
        "voornaam": voornaam,
        "achternaam": achternaam,
        "email": email,
        "warning_type": warning_type,
        "waarschuwing": waarschuwing
    }


def _build_warning_message(student_data: Dict[str, Any], warning_type: str) -> str:
    """Build a human-readable warning message based on warning type."""
    if warning_type == 'FAIL_adviesrapport':
        totaal = student_data.get('Totaal_aantal_SP', student_data.get('Totaal aantal SP', 'N/A'))
        vereist = student_data.get('Aantal_SP_vereist', student_data.get('Aantal SP vereist', 'N/A'))
        return f"FAIL status op adviesrapport (SP: {totaal}/{vereist})"
    
    elif warning_type == 'SP_mismatch_predelib':
        totaal = student_data.get('Totaal_aantal_SP', student_data.get('Totaal aantal SP', 'N/A'))
        vereist = student_data.get('Aantal_SP_vereist', student_data.get('Aantal SP vereist', 'N/A'))
        return f"SP waarden komen niet overeen in predeliberatierapport: {totaal} (totaal) vs {vereist} (vereist)"
    
    elif warning_type == 'SP_mismatch_dashboard':
        predelib_sp = student_data.get('Predelib_SP', 'N/A')
        dashboard_sp = student_data.get('Dashboard_SP', 'N/A')
        return f"SP verschilt tussen predelib ({predelib_sp}) en dashboard ({dashboard_sp})"
    
    return student_data.get('Waarschuwing', 'Onbekende waarschuwing')


def format_results(legacy_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert legacy results format to the new standardized format.
    
    Args:
        legacy_results: Results dictionary from data_processor.process_files()
    
    Returns:
        Standardized result dictionary matching the target schema
    """
    warnings = []
    
    # Process FAIL adviesrapport students
    for student in legacy_results.get('students_with_fail', []):
        warnings.append(format_warning(student, 'FAIL_adviesrapport'))
    
    # Process SP mismatch in predelib file
    for student in legacy_results.get('students_with_mismatching_SP_values_predelib', []):
        warnings.append(format_warning(student, 'SP_mismatch_predelib'))
    
    # Process SP mismatch between predelib and dashboard
    for mismatch in legacy_results.get('mismatches', []):
        warnings.append(format_warning(mismatch, 'SP_mismatch_dashboard'))
    
    return {
        "status": "success" if legacy_results.get('status') == 'completed' else "error",
        "summary": {
            "predelib_file": legacy_results.get('predelib_file', ''),
            "dashboard_file": legacy_results.get('dashboard_file', ''),
            "predelib_records": legacy_results.get('predelib_records', 0),
            "dashboard_records": legacy_results.get('dashboard_records', 0),
            "total_warnings": len(warnings),
            "fail_adviesrapport_count": legacy_results.get('students_with_fail_count', 0),
            "sp_mismatch_predelib_count": legacy_results.get('students_with_mismatching_SP_values_predelib_count', 0),
            "sp_mismatch_dashboard_count": legacy_results.get('mismatches_count', 0)
        },
        "warnings": warnings
    }