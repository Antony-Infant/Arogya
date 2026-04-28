"""
Symptom Extractor - Uses LLM to extract symptoms from patient messages.
No regex, no rule-based logic - pure LLM extraction.
"""
from .prompt_templates import PromptTemplates

class SymptomExtractor:
    def __init__(self):
        self.prompts = PromptTemplates()

    def extract(self, message: str, existing_symptoms: list, llm) -> list:
        """Extract new symptoms from patient message using LLM."""
        prompt = self.prompts.symptom_extraction_prompt(message, existing_symptoms)
        response = llm.generate(prompt, self.prompts.SYSTEM_PROMPT, temperature=0.1)

        if 'no new symptoms' in response.lower():
            return []

        symptoms = []
        existing_lower = [s.lower() for s in existing_symptoms]

        for line in response.strip().split('\n'):
            line = line.strip().lstrip('-•*').strip()
            if not line or len(line) < 3 or len(line) > 200:
                continue

            # Parse symptom with optional details
            sym_data = self._parse_symptom_line(line)
            if sym_data and sym_data['name'].lower() not in existing_lower:
                symptoms.append(sym_data)

        return symptoms[:10]

    def _parse_symptom_line(self, line: str) -> dict:
        """Parse a symptom line like 'Headache (severe, 3 days, frontal)'."""
        name = line
        severity = None
        duration = None

        if '(' in line and ')' in line:
            name = line[:line.index('(')].strip()
            details = line[line.index('(')+1:line.index(')')].strip()

            for detail in details.split(','):
                detail = detail.strip().lower()
                if detail in ('mild', 'moderate', 'severe'):
                    severity = detail
                elif any(word in detail for word in ['day', 'week', 'month', 'hour', 'year', 'since', 'morning']):
                    duration = detail

        if len(name) < 3:
            return None

        return {
            'name': name,
            'severity': severity,
            'duration': duration,
        }
