import re

def parse_query(query: str):
    """
    Parse medical insurance query to extract age, gender, procedure, location, and policy duration.
    
    Args:
        query (str): Raw query string
        
    Returns:
        dict: Parsed information with keys: raw_query, age, gender, procedure, location, policy_duration_months
    """
    parsed = {
        "raw_query": query,
        "age": None,
        "gender": None,
        "procedure": None,
        "location": None,
        "policy_duration_months": None
    }
    
    # Handle empty or None input
    if not query or not isinstance(query, str):
        return parsed
    
    q_lower = query.lower().strip()
    
    # --- Age + Gender Parsing ---
    age_gender_patterns = [
        # Pattern 1: 46M, 25F (with optional spaces and separators)
        r"\b(\d{1,3})\s*[/\-,]?\s*([mf])(?![a-z])\b",
        
        # Pattern 2: 46 male, 25 female  
        r"\b(\d{1,3})\s+(male|female)\b",
        
        # Pattern 3: male 46, female 25
        r"\b(male|female)\s+(\d{1,3})\b",
        
        # Pattern 4: age 46 male, age: 25, female
        r"\bage[:\s]*(\d{1,3})[,\s]*(male|female)?\b",
        
        # Pattern 5: male, age 46 or female age: 25
        r"\b(male|female)[,\s]*age[:\s]*(\d{1,3})\b"
    ]
    
    for i, pattern in enumerate(age_gender_patterns):
        match = re.search(pattern, q_lower)
        if match:
            group1, group2 = match.groups()
            
            # Handle different pattern structures
            if i in [0, 1, 3]:  # age comes first
                if group1.isdigit():
                    age = int(group1)
                    if 0 <= age <= 120:  # Reasonable age range
                        parsed["age"] = age
                        if group2:
                            if group2.lower().startswith('m'):
                                parsed["gender"] = "Male"
                            elif group2.lower().startswith('f'):
                                parsed["gender"] = "Female"
            elif i in [2, 4]:  # gender comes first
                if group2 and group2.isdigit():
                    age = int(group2)
                    if 0 <= age <= 120:
                        parsed["age"] = age
                        if group1.lower().startswith('m'):
                            parsed["gender"] = "Male"
                        elif group1.lower().startswith('f'):
                            parsed["gender"] = "Female"
            break
    
    # If age/gender not found together, try to find them separately
    if parsed["age"] is None:
        age_only_patterns = [
            r"\bage[:\s]*(\d{1,3})\b",
            r"\b(\d{1,3})\s*(?:years?|yrs?)\s*old\b",
            r"\b(\d{1,3})\s*yo\b"  # years old abbreviation
        ]
        for pattern in age_only_patterns:
            match = re.search(pattern, q_lower)
            if match:
                age = int(match.group(1))
                if 0 <= age <= 120:
                    parsed["age"] = age
                    break
    
    if parsed["gender"] is None:
        gender_patterns = [
            r"\b(male|female)\b",
            r"\b([mf])(?![a-z])\b"
        ]
        for pattern in gender_patterns:
            match = re.search(pattern, q_lower)
            if match:
                gender_str = match.group(1).lower()
                if gender_str in ['male', 'm']:
                    parsed["gender"] = "Male"
                elif gender_str in ['female', 'f']:
                    parsed["gender"] = "Female"
                break
    
    # --- Policy Duration Parsing ---
    duration_patterns = [
        # Handle various formats: 3-month, 6 months, 1year, 2 yrs, 30 days
        r"\b(\d+)\s*[-]?\s*(months?|mo(?:nth)?(?!le)|years?|yrs?|days?)\s*(?:policy|plan|coverage)?\b",
        r"\b(?:policy|plan|coverage)\s*(?:of|for)?\s*(\d+)\s*(months?|mo(?:nth)?(?!le)|years?|yrs?|days?)\b",
        r"\b(\d+)\s*[-]?\s*(m(?!ale|ore)|y(?!oung)|d)\s*(?:policy|plan)?\b"  # Short forms but avoid 'male', 'more', 'young'
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, q_lower)
        if match:
            try:
                num = int(match.group(1))
                unit = match.group(2).lower() if len(match.groups()) > 1 else ""
                
                # Convert to months
                if any(keyword in unit for keyword in ['year', 'yr', 'y']):
                    parsed["policy_duration_months"] = num * 12
                elif any(keyword in unit for keyword in ['day', 'd']):
                    parsed["policy_duration_months"] = max(1, round(num / 30))
                else:  # months, mo, month, m
                    parsed["policy_duration_months"] = num
                break
            except (ValueError, IndexError):
                continue
    
    # --- Location Parsing ---
    # Expanded city list with common variations
    cities_mapping = {
        "pune": "Pune", "mumbai": "Mumbai", "delhi": "Delhi", "new delhi": "Delhi",
        "bangalore": "Bangalore", "bengaluru": "Bangalore", "chennai": "Chennai",
        "kolkata": "Kolkata", "calcutta": "Kolkata", "hyderabad": "Hyderabad",
        "ahmedabad": "Ahmedabad", "surat": "Surat", "jaipur": "Jaipur",
        "lucknow": "Lucknow", "kanpur": "Kanpur", "nagpur": "Nagpur",
        "indore": "Indore", "thane": "Thane", "bhopal": "Bhopal",
        "visakhapatnam": "Visakhapatnam", "pimpri": "Pimpri", "patna": "Patna",
        "vadodara": "Vadodara", "ghaziabad": "Ghaziabad", "ludhiana": "Ludhiana",
        "agra": "Agra", "nashik": "Nashik", "faridabad": "Faridabad",
        "meerut": "Meerut", "rajkot": "Rajkot"
    }
    
    # Look for city names (prioritize longer matches first)
    sorted_cities = sorted(cities_mapping.keys(), key=len, reverse=True)
    for city in sorted_cities:
        # Use word boundaries to avoid partial matches
        pattern = rf"\b{re.escape(city)}\b"
        if re.search(pattern, q_lower):
            parsed["location"] = cities_mapping[city]
            break
    
    # --- Procedure Parsing ---
    # Enhanced procedure detection with better keyword grouping
    medical_keywords = {
        'surgery': ['surgery', 'surgical', 'operation', 'operative'],
        'replacement': ['replacement', 'implant', 'prosthetic'],
        'reconstruction': ['reconstruction', 'reconstructive', 'repair'],
        'treatment': ['treatment', 'therapy', 'therapeutic'],
        'diagnostic': ['biopsy', 'scan', 'test', 'screening', 'examination'],
        'cardiac': ['angioplasty', 'bypass', 'stent', 'cardiac'],
        'transplant': ['transplant', 'transplantation'],
        'procedure': ['procedure', 'intervention']
    }
    
    # Flatten all keywords
    all_keywords = []
    for category in medical_keywords.values():
        all_keywords.extend(category)
    
    # Look for procedure patterns
    procedure_patterns = [
        # Pattern 1: body_part + procedure (e.g., "knee surgery", "heart surgery")
        rf"\b([a-z]+)\s+({'|'.join(all_keywords)})\b",
        
        # Pattern 2: procedure + of + body_part (e.g., "surgery of knee")
        rf"\b({'|'.join(all_keywords)})\s+(?:of|on|for)\s+([a-z]+)\b",
        
        # Pattern 3: specific procedures (e.g., "angioplasty", "biopsy")
        rf"\b({'|'.join(all_keywords)})\b",
        
        # Pattern 4: complex procedures (e.g., "knee replacement surgery")
        rf"\b([a-z]+\s+(?:replacement|reconstruction|repair)(?:\s+surgery)?)\b"
    ]
    
    best_procedure = None
    best_length = 0
    
    for pattern in procedure_patterns:
        matches = re.finditer(pattern, q_lower)
        for match in matches:
            procedure_text = match.group(0).strip()
            # Prefer longer, more specific matches
            if len(procedure_text) > best_length:
                best_procedure = procedure_text
                best_length = len(procedure_text)
    
    if best_procedure:
        # Clean up the procedure text
        parsed["procedure"] = ' '.join(best_procedure.split()).title()
    
    return parsed


# Test cases to verify functionality
