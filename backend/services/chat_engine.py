
import logging
from .llm_service import OllamaService
from .causal_engine import CausalEngine
from .rag_engine import RAGEngine
from .symptom_extractor import SymptomExtractor

logger = logging.getLogger(__name__)

SYSTEM_DOCTOR = (
    "You are Arogya, a senior medical doctor conducting a patient consultation. "
    "You are warm, empathetic, thorough, and professional.\n\n"
    "RULES:\n"
    "- Keep responses to 2-4 sentences during information gathering\n"
    "- Ask ONE focused clinical question at a time\n"
    "- Be conversational and natural, not robotic\n"
    "- If the patient greets you, welcome them warmly and ask what brings them in\n"
    "- If they say thanks or bye after diagnosis, respond warmly and briefly\n"
    "- If they ask a general health question (like 'what is diabetes'), answer it "
    "directly and thoroughly. Do NOT start a symptom consultation.\n"
    "- Never use emojis\n"
    "- After gathering enough information, ask: 'Is there anything else you are "
    "experiencing, or shall I proceed with my assessment?'\n"
    "- Only diagnose when the patient confirms they have shared everything"
)

READINESS_CHECK = (
    "Based on this conversation, reply ONLY with the word READY or NOT_READY.\n"
    "READY = the patient has described AT LEAST 2 distinct symptoms AND has explicitly "
    "confirmed they are done sharing (e.g. 'that\\'s all', 'nothing else', 'no other symptoms', "
    "'please diagnose', 'go ahead', 'proceed', 'yes that\\'s everything').\n"
    "NOT_READY = still gathering information, OR the patient has not explicitly confirmed "
    "they are done, OR fewer than 2 symptoms have been described.\n"
    "When in doubt, reply NOT_READY."
)


class ChatEngine:
    def __init__(self):
        self.llm = OllamaService()
        self.causal = CausalEngine()
        self.rag = RAGEngine()
        self.extractor = SymptomExtractor()
        self._lat = None  # set by views.py
        self._lng = None

    def process_message(self, session, content, input_type, user):
        """Main entry. Always returns a dict with 'message' key. Never crashes."""
        try:
            return self._process(session, content, input_type, user)
        except Exception as e:
            logger.error(f"ChatEngine._process failed: {e}", exc_info=True)
            return {
                'message': 'I apologize, something went wrong on my end. Could you please repeat what you said?',
                'diagnosis': None, 'symptoms': [], 'follow_up_needed': True,
                'hospitals': [], 'tts_url': None,
            }

    def _process(self, session, content, input_type, user):
        from apps.chat.models import Message, ExtractedSymptom

        # Load conversation history as real turns
        db_msgs = list(
            Message.objects.filter(session=session)
            .order_by('created_at').values('role', 'content')[:30]
        )

        # Get known symptoms
        existing = list(session.extracted_symptoms.values_list('symptom_name', flat=True))

        # Extract new symptoms
        try:
            new_syms = self.extractor.extract(content, existing, self.llm)
            for s in new_syms:
                ExtractedSymptom.objects.get_or_create(
                    session=session,
                    symptom_name=s['name'],
                    defaults={
                        'severity': s.get('severity'),
                        'duration': s.get('duration'),
                        'body_location': s.get('location'),
                    }
                )
        except Exception as e:
            logger.warning(f"Symptom extraction failed: {e}")
            new_syms = []

        all_symptoms = existing + [s['name'] for s in new_syms]

        # Post-diagnosis chat
        if getattr(session, 'is_diagnosis_complete', False):
            return self._post_chat(db_msgs, content)

        # Build patient profile
        profile = self._build_profile(user, all_symptoms)

        # LLM decides if ready to diagnose
        # Require at least 5 messages (2-3 exchanges) and 2 distinct symptoms
        # before even asking the LLM readiness check - prevents premature diagnosis
        if len(db_msgs) >= 5 and len(all_symptoms) >= 2:
            try:
                if self._check_readiness(db_msgs, all_symptoms):
                    return self._diagnose(session, all_symptoms, db_msgs, user, profile)
            except Exception as e:
                logger.warning(f"Readiness check failed: {e}")

        # Bug 2 fix: Find hospitals early (during conversation, not just at diagnosis)
        # This way, as soon as the user has granted location, the frontend can show nearby doctors
        hospitals_early = self._find_hospitals(user)

        # Multi-turn doctor conversation
        messages = [{'role': 'system', 'content': SYSTEM_DOCTOR + '\n\n' + profile}]
        for m in db_msgs[-14:]:
            role = 'assistant' if m['role'] == 'assistant' else 'user'
            messages.append({'role': role, 'content': m['content'][:600]})

        return {
            'message': self.llm.chat(messages),
            'diagnosis': None,
            'symptoms': [s['name'] for s in new_syms],
            'follow_up_needed': True,
            'hospitals': hospitals_early,
            'tts_url': None,
        }

    def _build_profile(self, user, symptoms):
        parts = ['PATIENT CONTEXT:']
        try:
            if user:
                if getattr(user, 'gender', None):
                    parts.append(f"Gender: {user.gender}")
                if getattr(user, 'date_of_birth', None):
                    from datetime import date
                    age = date.today().year - user.date_of_birth.year
                    parts.append(f"Age: {age}")
                if getattr(user, 'existing_conditions', None):
                    parts.append(f"Pre-existing conditions: {user.existing_conditions}")
                if getattr(user, 'current_medications', None):
                    parts.append(f"Current medications: {user.current_medications}")
        except Exception:
            pass
        if symptoms:
            parts.append(f"Symptoms identified so far: {', '.join(symptoms)}")
        return '\n'.join(parts)

    def _check_readiness(self, history, symptoms):
        conv = '\n'.join([
            f"{'Doctor' if m['role'] == 'assistant' else 'Patient'}: {m['content'][:200]}"
            for m in history[-8:]
        ])
        prompt = f"Conversation:\n{conv}\n\nSymptoms identified: {', '.join(symptoms)}\n\n{READINESS_CHECK}"
        result = self.llm.generate(prompt, temperature=0.05).strip().upper()
        ready = 'READY' in result and 'NOT_READY' not in result
        logger.info(f"Diagnosis readiness: {'READY' if ready else 'NOT READY'}")
        return ready

    def _post_chat(self, history, content):
        messages = [{'role': 'system', 'content':
            'You are Arogya. The patient already received their diagnosis. '
            'Answer any follow-up questions briefly. If they say thanks or bye, wish them well. '
            'Do not repeat the full diagnosis. No emojis.'}]
        for m in history[-6:]:
            messages.append({
                'role': 'assistant' if m['role'] == 'assistant' else 'user',
                'content': m['content'][:300]
            })
        return {
            'message': self.llm.chat(messages),
            'diagnosis': None, 'symptoms': [], 'follow_up_needed': False,
            'hospitals': [], 'tts_url': None,
        }

    def _diagnose(self, session, symptoms, history, user, profile):
        from apps.diagnosis.models import DiseasePrediction

        # Run causal prediction
        try:
            predictions = self.causal.predict(symptoms, top_k=5)
        except Exception as e:
            logger.error(f"Causal prediction failed: {e}")
            predictions = []

        # Run RAG
        try:
            rag_results = self.rag.retrieve_for_symptoms(symptoms)
            rag_text = '\n---\n'.join([r['content'][:500] for r in rag_results[:3]])
        except Exception as e:
            logger.warning(f"RAG failed: {e}")
            rag_text = ''

        hospitals = self._find_hospitals(user)

        # No causal match - use RAG + LLM only
        if not predictions:
            logger.info("No causal match - RAG-only diagnosis")
            messages = [{'role': 'system', 'content':
                'You are Arogya. Provide your best medical assessment. '
                'Include: possible conditions, urgency level, recommended medicines with dosages, '
                'diet advice, home remedies, when to see a doctor, which specialist to consult. '
                'Be honest if uncertain. No emojis.\n\n'
                f'{profile}\n\nMedical Knowledge:\n{rag_text[:2000]}'}]
            for m in history[-6:]:
                messages.append({
                    'role': 'assistant' if m['role'] == 'assistant' else 'user',
                    'content': m['content'][:300]
                })
            messages.append({'role': 'user', 'content':
                f'Based on my symptoms ({", ".join(symptoms)}), what is your assessment?'})
            return {
                'message': self.llm.chat(messages),
                'diagnosis': None, 'symptoms': symptoms,
                'follow_up_needed': False, 'hospitals': hospitals, 'tts_url': None,
            }

        top = predictions[0]
        dd = top.get('disease_data', {})

        # DoWhy analysis
        try:
            causal_details = self.causal.dowhy_analysis(symptoms, top['disease_name'])
        except Exception as e:
            causal_details = f"Causal graph scoring used. ({e})"

        # Build diagnosis prompt
        diag_prompt = (
            f"Generate a comprehensive medical diagnosis.\n\n"
            f"{profile}\n\n"
            f"CAUSAL AI RESULT: {top['disease_name']} ({top['confidence']:.0%} confidence)\n"
            f"Causal Reasoning: {top['explanation']}\n"
            f"DoWhy Analysis: {causal_details}\n\n"
            f"MEDICAL KNOWLEDGE:\n{rag_text[:1500]}\n\n"
            f"DISEASE DATA:\n"
            f"Urgency: {dd.get('urgency_level', 'N/A')}\n"
            f"Specialist: {dd.get('specialist_type', 'N/A')}\n"
            f"Medicines: {dd.get('recommended_medicines', 'N/A')}\n"
            f"Diet: {dd.get('diet_recommendations', 'N/A')}\n"
            f"Home Remedies: {dd.get('home_remedies', 'N/A')}\n"
            f"Exercise: {dd.get('exercise_recommendations', 'N/A')}\n"
            f"Red Flags: {dd.get('red_flags', 'N/A')}\n\n"
            f"Format with ** bold headers **:\n"
            f"**Diagnosis** | **Clinical Reasoning** | **Urgency** | "
            f"**Recommended Medicines** | **Diet** | **Home Care** | "
            f"**Physical Activity** | **Red Flags** | **Specialist**\n"
            f"End with: This is AI-generated guidance. Please consult a qualified doctor."
        )

        diag_system = (
            "You are Arogya generating a comprehensive evidence-based diagnosis. "
            "Reference the patient's specific symptoms. Be thorough but clear. No emojis."
        )

        response = self.llm.generate(diag_prompt, diag_system, temperature=0.3)

        # Save prediction
        try:
            pred = DiseasePrediction.objects.create(
                session=session,
                user=user,
                disease_name=top['disease_name'],
                disease_id=top.get('disease_id', ''),
                confidence_score=top['confidence'],
                causal_explanation=top['explanation'] + '\nDoWhy: ' + causal_details,
                symptoms_matched='|'.join(top.get('matched_symptoms', [])),
                causal_weights_used='|'.join(top.get('causal_weights', [])),
                urgency_level=str(dd.get('urgency_level', '')),
                specialist_type=str(dd.get('specialist_type', '')),
                recommended_medicines=str(dd.get('recommended_medicines', '')),
                diet_recommendations=str(dd.get('diet_recommendations', '')),
                home_remedies=str(dd.get('home_remedies', '')),
                exercise_recommendations=str(dd.get('exercise_recommendations', '')),
                lifestyle_changes=str(dd.get('lifestyle_changes', '')),
                precautions=str(dd.get('precautions', '')),
                when_to_see_doctor=str(dd.get('red_flags', '')),
                complications_if_untreated=str(dd.get('complications_if_untreated', '')),
                rag_context_used=rag_text[:2000],
                alternative_diseases=[
                    {'disease': p['disease_name'], 'confidence': p['confidence']}
                    for p in predictions[1:4]
                ],
            )
            pred_id = pred.id
        except Exception as e:
            logger.error(f"Saving prediction failed: {e}")
            pred_id = None

        # Mark session complete
        try:
            session.is_diagnosis_complete = True
            session.save(update_fields=['is_diagnosis_complete'])
        except Exception as e:
            logger.warning(f"Could not mark session complete: {e}")

        diag_data = {
            'prediction_id': pred_id,
            'disease': top['disease_name'],
            'disease_id': top.get('disease_id', ''),
            'confidence': top['confidence'],
            'explanation': top['explanation'],
            'causal_analysis': causal_details,
            'urgency': str(dd.get('urgency_level', '')),
            'specialist': str(dd.get('specialist_type', '')),
            'medicines': str(dd.get('recommended_medicines', '')),
            'diet': str(dd.get('diet_recommendations', '')),
            'remedies': str(dd.get('home_remedies', '')),
            'exercise': str(dd.get('exercise_recommendations', '')),
            'precautions': str(dd.get('precautions', '')),
            'when_to_see_doctor': str(dd.get('red_flags', '')),
            'complications': str(dd.get('complications_if_untreated', '')),
            'lifestyle': str(dd.get('lifestyle_changes', '')),
            'alternatives': [
                {'disease': p['disease_name'], 'confidence': p['confidence']}
                for p in predictions[1:4]
            ],
        }

        return {
            'message': response,
            'diagnosis': diag_data,
            'symptoms': symptoms,
            'follow_up_needed': False,
            'hospitals': hospitals,
            'tts_url': None,
        }

    def _find_hospitals(self, user):
        try:
            lat = self._lat or getattr(user, 'location_lat', None)
            lng = self._lng or getattr(user, 'location_lng', None)
            if not lat or not lng:
                logger.info("No GPS coords - hospitals skipped")
                return []
            from .hospital_service import find_nearby_hospitals
            return find_nearby_hospitals(float(lat), float(lng))
        except Exception as e:
            logger.warning(f"Hospital search failed: {e}")
            return []
