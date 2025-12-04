import json
import logging
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class LLMProvider:
    """Abstract LLM provider interface"""
    
    async def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract structured fields from contract text"""
        raise NotImplementedError
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer question based on context"""
        raise NotImplementedError
    
    async def detect_risks(self, text: str) -> List[Dict[str, Any]]:
        """Detect risky clauses"""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI-based LLM provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.api_key = api_key
        self.model = model
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=api_key)
        except ImportError:
            logger.error("OpenAI client not available")
            raise
    
    async def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract structured fields using OpenAI"""
        extraction_prompt = f"""
        Extract the following fields from this contract. Return valid JSON only.
        
        Fields to extract:
        - parties: List of party names
        - effective_date: Start date of contract
        - term: Contract duration/term
        - governing_law: Governing law clause
        - payment_terms: Payment terms/conditions
        - termination: Termination clause
        - auto_renewal: Auto-renewal terms
        - confidentiality: Confidentiality/NDA terms
        - indemnity: Indemnification clause
        - liability_cap: Liability cap (with amount and currency)
        - signatories: List of signatories with names and titles
        
        Contract text:
        {text[:4000]}
        
        Return ONLY valid JSON, no other text.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a contract analysis expert. Extract fields and return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            # Clean up JSON
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            return json.loads(result_text)
        except Exception as e:
            logger.error(f"OpenAI extraction failed: {str(e)}")
            return {}
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer question using OpenAI"""
        qa_prompt = f"""
        Based ONLY on the following contract text, answer the question.
        If the answer is not in the text, say "Not found in contract".
        
        Context:
        {context}
        
        Question: {question}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a contract analysis expert. Answer based only on provided contract text."},
                    {"role": "user", "content": qa_prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI QA failed: {str(e)}")
            return f"Error: {str(e)}"
    
    async def detect_risks(self, text: str) -> List[Dict[str, Any]]:
        """Detect risky clauses using OpenAI"""
        risk_prompt = f"""
        Analyze this contract for risky clauses. Return a JSON array of findings.
        
        Specifically look for:
        - Auto-renewal with less than 30 days notice
        - Unlimited liability clauses
        - Broad indemnification requirements
        - Unfavorable payment terms
        - Restrictive termination clauses
        - Excessive confidentiality restrictions
        
        Each finding should have:
        - clause_type: Type of risky clause
        - severity: "critical", "high", "medium", "low"
        - description: What makes it risky
        - evidence: Relevant text snippet
        - recommendation: How to mitigate
        
        Contract text:
        {text[:4000]}
        
        Return ONLY valid JSON array, no other text.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a contract risk analysis expert. Identify risky clauses and return valid JSON."},
                    {"role": "user", "content": risk_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            # Clean up JSON
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            
            return json.loads(result_text)
        except Exception as e:
            logger.error(f"OpenAI risk detection failed: {str(e)}")
            return []


class LocalLLMProvider(LLMProvider):
    """Fallback local LLM provider using regex patterns"""
    
    async def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract fields using regex patterns"""
        import re
        
        fields = {
            "parties": self._extract_parties(text),
            "effective_date": self._extract_date(text),
            "governing_law": self._extract_governing_law(text),
            "payment_terms": self._extract_payment_terms(text),
            "liability_cap": self._extract_liability_cap(text),
        }
        return fields
    
    async def answer_question(self, question: str, context: str) -> str:
        """Answer question using simple keyword matching"""
        import re
        
        # Simple keyword search
        question_lower = question.lower()
        context_lower = context.lower()
        
        if "who" in question_lower and "party" in question_lower:
            return self._extract_parties_as_text(context)
        
        # Search for relevant sentences
        sentences = context.split(".")
        relevant = [s for s in sentences if any(w in s.lower() for w in question_lower.split())]
        if relevant:
            return " ".join(relevant[:3])
        
        return "Information not found in contract"
    
    async def detect_risks(self, text: str) -> List[Dict[str, Any]]:
        """Detect risks using pattern matching"""
        import re
        
        risks = []
        
        # Check for unlimited liability
        if re.search(r"unlimited\s+liability|liability\s+is\s+unlimited", text, re.IGNORECASE):
            risks.append({
                "clause_type": "Unlimited Liability",
                "severity": "critical",
                "description": "Contract contains unlimited liability clause",
                "evidence": self._find_phrase(text, "unlimited liability"),
                "recommendation": "Negotiate a cap on liability exposure"
            })
        
        # Check for auto-renewal
        if re.search(r"auto.?renew|automatically\s+renew", text, re.IGNORECASE):
            risks.append({
                "clause_type": "Auto-Renewal",
                "severity": "high",
                "description": "Auto-renewal clause found",
                "evidence": self._find_phrase(text, "auto-renewal"),
                "recommendation": "Ensure adequate notice period (30+ days)"
            })
        
        return risks
    
    def _extract_parties(self, text: str) -> List[str]:
        """Extract party names"""
        import re
        parties = []
        # Look for "between X and Y"
        match = re.search(r"between\s+([^,]+)\s+and\s+([^,]+)", text, re.IGNORECASE)
        if match:
            parties = [match.group(1).strip(), match.group(2).strip()]
        return parties
    
    def _extract_parties_as_text(self, text: str) -> str:
        """Extract parties as readable text"""
        parties = self._extract_parties(text)
        return ", ".join(parties) if parties else "Parties not identified"
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract effective date"""
        import re
        match = re.search(r"effective\s+(?:as of\s+|date\s+)?(\d{1,2}[/-]\d{1,2}[/-]\d{4})", text, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _extract_governing_law(self, text: str) -> Optional[str]:
        """Extract governing law"""
        import re
        match = re.search(r"(?:governed|construed|interpreted)\s+(?:by|under)\s+(?:the\s+)?laws?\s+of\s+([^.,]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_payment_terms(self, text: str) -> Optional[str]:
        """Extract payment terms"""
        import re
        match = re.search(r"payment\s+(?:terms?|due|within)\s+([^.,]+)", text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_liability_cap(self, text: str) -> Optional[Dict[str, str]]:
        """Extract liability cap"""
        import re
        match = re.search(r"(?:cap|limit|maximum|liable)\s+(?:on\s+)?(?:liability|damages)\s+(?:of|to)?\s+(\$|£|€)?([0-9,]+(?:\.\d+)?)", text, re.IGNORECASE)
        if match:
            return {
                "amount": match.group(2),
                "currency": match.group(1) or "USD"
            }
        return None
    
    def _find_phrase(self, text: str, phrase: str) -> str:
        """Find and return phrase with context"""
        import re
        pattern = rf".{{0,100}}{re.escape(phrase)}.{{0,100}}"
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(0).strip() if match else phrase


def get_llm_provider(provider_type: str, api_key: str = "", model: str = "") -> LLMProvider:
    """Factory function to get LLM provider"""
    if provider_type == "openai" and api_key:
        return OpenAIProvider(api_key, model)
    else:
        logger.warning("Using local LLM provider (limited functionality)")
        return LocalLLMProvider()
