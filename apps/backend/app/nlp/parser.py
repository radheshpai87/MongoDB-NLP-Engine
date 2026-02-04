import re
from typing import Dict, Any, Optional

class NLPQueryParser:
    """Simple NLP parser to convert natural language to MongoDB queries"""
    
    def __init__(self):
        self.operators = {
            "greater than": "$gt",
            "more than": "$gt",
            "above": "$gt",
            "over": "$gt",
            "less than": "$lt",
            "fewer than": "$lt",
            "below": "$lt",
            "under": "$lt",
            "equal to": "$eq",
            "equals": "$eq",
            "is": "$eq",
            "at least": "$gte",
            "minimum": "$gte",
            "at most": "$lte",
            "maximum": "$lte",
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
        
        # Check if this is an aggregation query
        agg_result = self._check_aggregation(query, collection_name)
        if agg_result:
            return agg_result
        
        # Extract field, operator, and value for filtering
        mongo_filter = {}
        extracted_field = None
        extracted_value = None
        
        # Pattern: field + operator + value
        for op_phrase, mongo_op in self.operators.items():
            if op_phrase in query:
                parts = query.split(op_phrase)
                if len(parts) == 2:
                    field = self._extract_field(parts[0])
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
                parts = re.split(r'\bcontains\b|\bwith\b', query)
                if len(parts) == 2:
                    field = self._extract_field(parts[0])
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
        
        # Common field mappings
        field_aliases = {
            "revenue": "revenue",
            "income": "revenue",
            "sales": "revenue",
            "earnings": "revenue",
            "employees": "employees",
            "staff": "employees",
            "workers": "employees",
            "people": "employees",
            "name": "name",
            "company": "name",
            "industry": "industry",
            "sector": "industry",
            "status": "status",
            "founded": "founded",
            "year": "founded",
        }
        
        for alias, field in field_aliases.items():
            if alias in text:
                return field
        
        # Try to extract last word as field name
        words = text.split()
        if words:
            last_word = words[-1].strip()
            return last_word if last_word else None
        
        return None
    
    def _extract_value(self, text: str) -> Any:
        """Extract value from text"""
        text = text.strip()
        
        # Remove common words
        text = re.sub(r'\b(show|display|get|find|list)\b', '', text, flags=re.IGNORECASE).strip()
        
        # Try to extract number
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
        
        # Return as string if not a number
        return text if text else None
