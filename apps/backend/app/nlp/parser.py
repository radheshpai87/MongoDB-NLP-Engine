import re
from typing import Dict, Any, Optional
from datetime import datetime

class NLPQueryParser:
    """Simple NLP parser to convert natural language to MongoDB queries"""
    
    def __init__(self):
        self.operators = {
            "greater than": "$gt",
            "more than": "$gt",
            "above": "$gt",
            "over": "$gt",
            "exceeds": "$gt",
            "higher than": "$gt",
            "less than": "$lt",
            "fewer than": "$lt",
            "below": "$lt",
            "under": "$lt",
            "lower than": "$lt",
            "equal to": "$eq",
            "equals": "$eq",
            "is": "$eq",
            "are": "$eq",
            "at least": "$gte",
            "minimum": "$gte",
            "minimum of": "$gte",
            "at most": "$lte",
            "maximum": "$lte",
            "maximum of": "$lte",
            "not equal": "$ne",
            "not": "$ne",
        }
        
        self.aggregation_keywords = {
            "count": "count",
            "total": "sum",
            "sum": "sum",
            "average": "avg",
            "avg": "avg",
            "mean": "avg",
            "maximum": "max",
            "max": "max",
            "minimum": "min",
            "min": "min",
            "highest": "max",
            "lowest": "min",
            "most": "max",
            "least": "min",
        }
        
        # Common field aliases - more comprehensive
        self.field_aliases = {
            "revenue": "revenue",
            "income": "revenue",
            "sales": "revenue",
            "earnings": "revenue",
            "profit": "revenue",
            "money": "revenue",
            "employees": "employees",
            "staff": "employees",
            "workers": "employees",
            "people": "employees",
            "headcount": "employees",
            "name": "name",
            "company": "name",
            "companies": "name",
            "industry": "industry",
            "sector": "industry",
            "field": "industry",
            "domain": "industry",
            "status": "status",
            "state": "status",
            "founded": "founded",
            "year": "founded",
            "established": "founded",
            "started": "founded",
            "created": "founded",
        }
        
    def parse(self, query: str, collection_name: str = "companies") -> Dict[str, Any]:
        """Parse natural language query into MongoDB filter or aggregation"""
        query = query.lower().strip()
        
        if not query:
            return {
                "collection": collection_name,
                "filter": {},
                "parsed_query": query,
                "error": "Empty query provided"
            }
        
        # Handle "all" or "everything" - return empty filter (matches all)
        if query in ["all", "everything", "all companies", "show all", "list all", "get all"]:
            return {
                "collection": collection_name,
                "filter": {},
                "parsed_query": query
            }
        
        # Check if this is an aggregation query
        agg_result = self._check_aggregation(query, collection_name)
        if agg_result:
            return agg_result
        
        # Extract field, operator, and value for filtering
        mongo_filter = {}
        extracted_field = None
        extracted_value = None
        
        # Pattern: "between X and Y" for ranges
        between_match = re.search(r'between\s+(\d+(?:[.,]\d+)?)\s*(?:and|to)\s+(\d+(?:[.,]\d+)?)', query)
        if between_match:
            field = self._extract_field_flexible(query)
            if field:
                min_val = float(between_match.group(1).replace(',', ''))
                max_val = float(between_match.group(2).replace(',', ''))
                extracted_field = field
                extracted_value = f"{min_val}-{max_val}"
                mongo_filter[field] = {"$gte": int(min_val) if min_val == int(min_val) else min_val,
                                       "$lte": int(max_val) if max_val == int(max_val) else max_val}
        
        # Pattern: "after/since/before [year]" (e.g., "founded after 2013", "after 2013")
        if not mongo_filter:
            year_pattern = re.search(r'\b(after|since|before)\s+(\d{4})', query)
            if year_pattern:
                operator = year_pattern.group(1)
                year = int(year_pattern.group(2))
                extracted_field = "founded"
                extracted_value = year
                
                if operator in ["after", "since"]:
                    # After/since means >= start of that year
                    mongo_filter["founded"] = {"$gte": datetime(year, 1, 1)}
                elif operator == "before":
                    # Before means < start of that year
                    mongo_filter["founded"] = {"$lt": datetime(year, 1, 1)}
        
        # Pattern: field + "in" + year (e.g., "founded in 2020")
        if not mongo_filter:
            in_year_match = re.search(r'\b(founded|year|established|started|created)\s+in\s+(\d{4})', query)
            if in_year_match:
                extracted_field = "founded"
                year = int(in_year_match.group(2))
                extracted_value = year
                # Match the year in the datetime field using datetime objects
                mongo_filter["founded"] = {
                    "$gte": datetime(year, 1, 1),
                    "$lt": datetime(year + 1, 1, 1)
                }
        
        # Pattern: "in [industry]" or "from [industry]"
        if not mongo_filter:
            industry_match = re.search(r'\b(in|from)\s+(technology|consulting|software|research|cloud computing|cybersecurity|agriculture|finance|[\w\s]+)\s+(industry|sector)?', query)
            if industry_match and "in" in query:
                industry = industry_match.group(2).strip()
                extracted_field = "industry"
                extracted_value = industry
                # Case-insensitive match
                mongo_filter["industry"] = {"$regex": industry, "$options": "i"}
        
        # Pattern: field + operator + value
        if not mongo_filter:
            for op_phrase, mongo_op in self.operators.items():
                if op_phrase in query:
                    parts = query.split(op_phrase, 1)
                    if len(parts) == 2:
                        field = self._extract_field_flexible(parts[0])
                        value = self._extract_value(parts[1])
                        extracted_field = field
                        extracted_value = value
                        
                        if field and value is not None:
                            if mongo_op == "$eq":
                                mongo_filter[field] = value
                            else:
                                mongo_filter[field] = {mongo_op: value}
                            break
        
        # Handle "contains" or "with" patterns
        if not mongo_filter:
            if "contains" in query or "with" in query:
                parts = re.split(r'\bcontains\b|\bwith\b', query, 1)
                if len(parts) == 2:
                    field = self._extract_field_flexible(parts[0])
                    value = self._extract_value(parts[1])
                    extracted_field = field
                    extracted_value = value
                    if field and value:
                        mongo_filter[field] = {"$regex": str(value), "$options": "i"}
        
        # Check if parsing failed
        if not mongo_filter:
            error_msg = self._generate_error_message(query, extracted_field, extracted_value)
            return {
                "collection": collection_name,
                "filter": {},
                "parsed_query": query,
                "error": error_msg
            }
        
        return {
            "collection": collection_name,
            "filter": mongo_filter,
            "parsed_query": query
        }
    
    def _check_aggregation(self, query: str, collection_name: str) -> Optional[Dict[str, Any]]:
        """Check if query is asking for aggregation (count, sum, total, etc.)"""
        for keyword, agg_type in self.aggregation_keywords.items():
            if keyword in query:
                field = self._extract_field(query)
                
                # Special case for count queries
                if agg_type == "count":
                    if not field or "all" in query:
                        # Count all documents
                        return {
                            "collection": collection_name,
                            "query_type": "aggregation",
                            "aggregation": {"type": "count", "field": None},
                            "parsed_query": query
                        }
                    else:
                        # Count specific field
                        return {
                            "collection": collection_name,
                            "query_type": "aggregation",
                            "aggregation": {"type": "count", "field": field},
                            "parsed_query": query
                        }
                
                # Check if query is asking for the document with max/min value
                # e.g., "company with most revenue", "company earning highest revenue"
                find_document = any(word in query for word in ["company", "companies", "which", "who", "show", "find", "get"])
                
                # For max/min - check if they want the document or just the value
                if agg_type in ["max", "min"] and find_document and field:
                    return {
                        "collection": collection_name,
                        "query_type": "find_extreme",
                        "aggregation": {"type": agg_type, "field": field},
                        "parsed_query": query
                    }
                
                # For sum, avg, max, min - need a field
                if field:
                    return {
                        "collection": collection_name,
                        "query_type": "aggregation",
                        "aggregation": {"type": agg_type, "field": field},
                        "parsed_query": query
                    }
        
        return None
    
    def _generate_error_message(self, query: str, field: Optional[str], value: Any) -> str:
        """Generate helpful error message based on what went wrong"""
        if not field:
            return f"Could not identify field in query: '{query}'. Try: 'revenue greater than 5000000' or 'total employees' or 'count all companies'"
        elif value is None:
            return f"Could not extract value from query: '{query}'. Please specify a numeric or text value"
        else:
            return f"Could not understand query pattern: '{query}'. Try: 'field greater than value' or 'field contains text'"
    
    def _extract_field(self, text: str) -> Optional[str]:
        """Extract field name from text"""
        text = text.strip()
        
        for alias, field in self.field_aliases.items():
            if alias in text:
                return field
        
        # Try to extract last word as field name
        words = text.split()
        if words:
            last_word = words[-1].strip()
            return last_word if last_word else None
        
        return None
    
    def _extract_field_flexible(self, text: str) -> Optional[str]:
        """Extract field name from text with flexible matching"""
        text = text.strip()
        
        # Check all known field aliases
        for alias, field in self.field_aliases.items():
            if alias in text:
                return field
        
        # If no match found, return None
        return None
    
    def _extract_value(self, text: str) -> Any:
        """Extract value from text"""
        text = text.strip()
        
        # Remove common words
        text = re.sub(r'\b(show|display|get|find|list|all|the)\b', '', text, flags=re.IGNORECASE).strip()
        
        # Try to extract number (including decimals, commas, and multipliers)
        number_match = re.search(r'(\d+(?:[.,]\d+)?)\s*(million|m|k|thousand)?', text, re.IGNORECASE)
        if number_match:
            num = float(number_match.group(1).replace(',', ''))
            multiplier = number_match.group(2)
            
            if multiplier:
                multiplier = multiplier.lower()
                if multiplier in ['million', 'm']:
                    num *= 1_000_000
                elif multiplier in ['k', 'thousand']:
                    num *= 1_000
            
            return int(num) if num == int(num) else num
        
        # Return as string if not a number (for text searches)
        return text if text else None
