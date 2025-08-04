import os
import re
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from typing import Dict, List, Any, Optional, Tuple
import parse as pr

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Assuming your parse module is available
try:
    import parse as prds
except ImportError:
    logger.warning("Parse module not found. Please ensure parse.py is available.")
    pr = None

class InsuranceClaimsProcessor:
    """
    A robust insurance claims processor that handles waiting periods and procedure coverage.
    """
    
    def __init__(self, clauses_file: str = "all_clauses.json", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the processor with clauses and model.
        
        Args:
            clauses_file: Path to JSON file containing all clauses
            model_name: Name of the sentence transformer model
        """
        self.clauses_file = clauses_file
        self.model_name = model_name
        self.all_clauses = []
        self.model = None
        
        # Load clauses and model
        self._load_clauses()
        self._load_model()
        self._ensure_embeddings()
    
    def _load_clauses(self):
        """Load clauses from JSON file with error handling."""
        try:
            if not os.path.exists(self.clauses_file):
                raise FileNotFoundError(f"Clauses file {self.clauses_file} not found")
                
            with open(self.clauses_file, "r", encoding="utf-8") as f:
                self.all_clauses = json.load(f)
            
            if not self.all_clauses:
                raise ValueError("No clauses found in the file")
                
            logger.info(f"✅ Loaded {len(self.all_clauses)} clauses")
            
        except Exception as e:
            logger.error(f"Error loading clauses: {e}")
            self.all_clauses = []
    
    def _load_model(self):
        """Load sentence transformer model with error handling."""
        try:
            self.model = SentenceTransformer(self.model_name, cache_folder="models")
            logger.info("✅ Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.model = None
    
    def _ensure_embeddings(self):
        """Compute embeddings if not present, with proper error handling."""
        if not self.all_clauses or not self.model:
            logger.warning("Cannot compute embeddings: missing clauses or model")
            return
        
        try:
            # Check if embeddings exist
            has_embeddings = all("embedding" in clause for clause in self.all_clauses)
            
            if not has_embeddings:
                logger.info("⏳ Computing embeddings for all clauses (first time)...")
                
                for i, clause in enumerate(self.all_clauses):
                    if "text" not in clause:
                        logger.warning(f"Clause {i} missing 'text' field, skipping")
                        continue
                        
                    try:
                        embedding = self.model.encode(clause["text"])
                        clause["embedding"] = embedding.tolist()
                    except Exception as e:
                        logger.error(f"Error computing embedding for clause {i}: {e}")
                        clause["embedding"] = []
                
                # Save embeddings
                try:
                    output_file = "all_clauses_with_embeddings.json"
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(self.all_clauses, f, ensure_ascii=False, indent=2)
                    logger.info(f"✅ Saved clauses with embeddings to {output_file}")
                except Exception as e:
                    logger.error(f"Error saving embeddings: {e}")
            else:
                logger.info("✅ Embeddings already present")
                
        except Exception as e:
            logger.error(f"Error in embedding process: {e}")

    def extract_waiting_periods(self, text: str) -> List[int]:
        """
        Extract all waiting periods in months from clause text.
        
        Args:
            text: Clause text to analyze
            
        Returns:
            List of waiting periods in months
        """
        if not text or not isinstance(text, str):
            return []
        
        periods = []
        
        # Enhanced pattern to catch more variations
        patterns = [
            r"(\d+)\s*(day|days|month|months|year|years|yr|yrs)",
            r"(\d+)[-]?(day|days|month|months|year|years|yr|yrs)",
            r"waiting\s+period\s+(?:of\s+)?(\d+)\s*(day|days|month|months|year|years|yr|yrs)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text.lower())
            for num_str, unit in matches:
                try:
                    num = int(num_str)
                    if num <= 0:  # Skip invalid numbers
                        continue
                        
                    if "year" in unit or "yr" in unit:
                        periods.append(num * 12)
                    elif "day" in unit:
                        periods.append(max(1, round(num / 30)))
                    else:  # month
                        periods.append(num)
                except ValueError:
                    continue
        
        return periods

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not self.model or not text1 or not text2:
            return 0.0
        
        try:
            emb1 = self.model.encode(text1)
            emb2 = self.model.encode(text2)
            
            # Compute cosine similarity
            similarity = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8
            )
            
            # Ensure result is between 0 and 1
            return max(0.0, min(1.0, float(similarity)))
            
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

    def check_waiting_period(self, parsed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check if policy duration meets waiting period requirements.
        
        Args:
            parsed: Parsed query information
            
        Returns:
            Rejection decision if waiting period not met, None otherwise
        """
        if (not parsed.get("policy_duration_months") or 
            not parsed.get("procedure") or
            not self.all_clauses):
            return None
        
        policy_duration = parsed["policy_duration_months"]
        procedure = parsed["procedure"].lower()
        
        # Extract key terms from procedure for better matching
        procedure_terms = set(procedure.split())
        
        waiting_periods = []
        relevant_clauses = []
        
        for clause in self.all_clauses:
            if "text" not in clause:
                continue
                
            clause_text = clause["text"].lower()
            
            # Check if clause mentions waiting period
            if "waiting period" not in clause_text:
                continue
            
            # Check if procedure is mentioned (flexible matching)
            procedure_mentioned = False
            for term in procedure_terms:
                if len(term) > 2 and term in clause_text:  # Avoid matching very short terms
                    procedure_mentioned = True
                    break
            
            # Also check semantic similarity for procedure matching
            if not procedure_mentioned and self.model:
                try:
                    similarity = self.compute_similarity(procedure, clause_text)
                    if similarity > 0.3:  # Lower threshold for waiting period checks
                        procedure_mentioned = True
                except Exception:
                    pass
            
            if procedure_mentioned:
                periods = self.extract_waiting_periods(clause_text)
                if periods:
                    waiting_periods.extend(periods)
                    relevant_clauses.append(clause["text"])
        
        if waiting_periods:
            min_required = min(waiting_periods)
            if policy_duration < min_required:
                return {
                    "decision": "rejected",
                    "justification": [
                        f"Policy active for {policy_duration} months but requires at least "
                        f"{min_required} months waiting period for '{parsed['procedure']}'."
                    ],
                    "clauses": relevant_clauses[:2],  # Limit to first 2 clauses
                    "confidence": 0.9
                }
        
        return None

    def check_procedure_coverage(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if procedure is covered using semantic similarity.
        
        Args:
            parsed: Parsed query information
            
        Returns:
            Decision dictionary with approval/rejection
        """
        if not parsed.get("procedure") or not self.all_clauses or not self.model:
            return {
                "decision": "needs_review",
                "justification": ["Cannot verify procedure coverage - missing information"],
                "clauses": [],
                "confidence": 0.0
            }
        
        procedure = parsed["procedure"]
        best_match = None
        best_score = 0.0
        
        # Find best matching clause using precomputed embeddings
        try:
            proc_emb = self.model.encode(procedure)
            
            for clause in self.all_clauses:
                if "embedding" not in clause or not clause["embedding"]:
                    continue
                
                try:
                    clause_emb = np.array(clause["embedding"])
                    
                    # Compute cosine similarity
                    similarity = np.dot(proc_emb, clause_emb) / (
                        np.linalg.norm(proc_emb) * np.linalg.norm(clause_emb) + 1e-8
                    )
                    
                    if similarity > best_score:
                        best_score = similarity
                        best_match = clause
                        
                except Exception as e:
                    logger.warning(f"Error computing similarity for clause: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error in procedure coverage check: {e}")
            return {
                "decision": "needs_review",
                "justification": ["Error in semantic analysis"],
                "clauses": [],
                "confidence": 0.0
            }
        
        # Make decision based on best match
        if best_match and best_score > 0.45:  # Reasonable similarity threshold
            clause_text = best_match["text"].lower()
            
            # Check for exclusion keywords
            exclusion_keywords = [
                "not covered", "excluded", "not payable", "not eligible",
                "except", "excluding", "does not cover", "shall not",
                "not applicable", "not included"
            ]
            
            is_excluded = any(keyword in clause_text for keyword in exclusion_keywords)
            
            if is_excluded:
                return {
                    "decision": "rejected",
                    "justification": [
                        f"Procedure '{procedure}' appears to be excluded based on policy terms "
                        f"(similarity: {best_score:.2f})"
                    ],
                    "clauses": [best_match["text"]],
                    "confidence": min(0.9, best_score + 0.1)
                }
            else:
                return {
                    "decision": "approved",
                    "justification": [
                        f"Procedure '{procedure}' is covered according to policy terms "
                        f"(similarity: {best_score:.2f})"
                    ],
                    "clauses": [best_match["text"]],
                    "confidence": best_score
                }
        
        elif best_match and best_score > 0.25:  # Lower confidence match
            return {
                "decision": "needs_review",
                "justification": [
                    f"Procedure '{procedure}' has potential coverage but requires manual review "
                    f"(similarity: {best_score:.2f})"
                ],
                "clauses": [best_match["text"]] if best_match else [],
                "confidence": best_score
            }
        
        else:
            return {
                "decision": "needs_review",
                "justification": [
                    f"Procedure '{procedure}' not found in policy terms - manual verification needed"
                ],
                "clauses": [],
                "confidence": 0.0
            }

    def make_decision(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make final decision on insurance claim based on parsed query.
        
        Args:
            parsed: Parsed query information
            
        Returns:
            Decision dictionary with justification and clauses
        """
        if not parsed:
            return {
                "decision": "needs_review",
                "justification": ["Invalid or empty query"],
                "clauses": [],
                "confidence": 0.0
            }
        
        # Step 1: Check waiting period (highest priority)
        waiting_decision = self.check_waiting_period(parsed)
        if waiting_decision:
            return waiting_decision
        
        # Step 2: Check procedure coverage
        coverage_decision = self.check_procedure_coverage(parsed)
        
        return coverage_decision

# Convenience functions for backward compatibility
def extract_waiting_periods(text: str) -> List[int]:
    """Legacy function - use InsuranceClaimsProcessor.extract_waiting_periods instead."""
    processor = InsuranceClaimsProcessor()
    return processor.extract_waiting_periods(text)

def make_decision(parsed: Dict[str, Any], all_clauses: List[Dict], model) -> Dict[str, Any]:
    """Legacy function - use InsuranceClaimsProcessor.make_decision instead."""
    # Create a temporary processor instance
    processor = InsuranceClaimsProcessor()
    processor.all_clauses = all_clauses
    processor.model = model
    return processor.make_decision(parsed)

# Example usage and testing
if __name__ == "__main__":
    # Initialize processor
    try:
        processor = InsuranceClaimsProcessor()
        
        user_query = input("Enter your insurance-related query: ")
        
        # Step 2: Parse the query
        parsed = pr.parse_query(user_query)
        print("\n📌 Parsed Query:", parsed)
        
        # Example parsed query
        sample_parsed = parsed
        
        # Make decision
        decision = processor.make_decision(sample_parsed)
        
        print("Sample Decision:")
        print(json.dumps(decision, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        print(f"Error: {e}")