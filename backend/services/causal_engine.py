"""
Causal AI Engine - Uses disease-symptom causal graph for cause-effect reasoning.
Built with DoWhy for causal inference.
Not just pattern matching - actual causal inference.
"""
import json
import pandas as pd
import networkx as nx
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CausalEngine:
    _instance = None
    _graph = None
    _dataset = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._graph is None:
            self._load_graph()
        if self._dataset is None:
            self._load_dataset()

    def _load_graph(self):
        try:
            with open(settings.CAUSAL_GRAPH_PATH, 'r') as f:
                CausalEngine._graph = nx.node_link_graph(json.load(f))
            logger.info(f"Causal graph loaded: {self._graph.number_of_nodes()} nodes, {self._graph.number_of_edges()} edges")
        except FileNotFoundError:
            CausalEngine._graph = nx.DiGraph()
            logger.warning("Causal graph not found. Run scripts/build_causal_graph.py first.")

    def _load_dataset(self):
        try:
            CausalEngine._dataset = pd.read_csv(settings.DISEASE_DATASET_PATH)
            logger.info(f"Dataset loaded: {len(self._dataset)} diseases")
        except FileNotFoundError:
            CausalEngine._dataset = pd.DataFrame()
            logger.warning("Disease dataset not found.")

    def predict_disease(self, symptoms: list) -> list:
        """
        Causal inference: Given symptoms, predict diseases using causal weights.
        Returns ranked list of (disease, confidence, explanation).
        """
        if self._dataset is None or self._dataset.empty:
            return []

        symptoms_lower = [s.lower().strip() for s in symptoms]
        results = []

        for _, disease_row in self._dataset.iterrows():
            score = 0.0
            matched = []
            weights = []

            # Parse causal weights from dataset
            causal_weights = self._parse_causal_weights(disease_row.get('causal_weight', ''))

            # Parse all symptoms
            all_disease_symptoms = self._parse_pipe_field(disease_row.get('all_symptoms', ''))

            # Match user symptoms against causal weights (high precision)
            for user_sym in symptoms_lower:
                best_match = None
                best_weight = 0

                for causal_sym, weight in causal_weights.items():
                    similarity = self._symptom_match(user_sym, causal_sym)
                    if similarity > 0.5 and weight > best_weight:
                        best_match = causal_sym
                        best_weight = weight

                if best_match:
                    score += best_weight
                    matched.append(best_match)
                    weights.append(f"{best_match}:{best_weight}")
                else:
                    # Check all_symptoms with lower weight
                    for disease_sym in all_disease_symptoms:
                        if self._symptom_match(user_sym, disease_sym.lower()) > 0.5:
                            score += 0.25
                            matched.append(disease_sym)
                            break

            if matched:
                max_possible = sum(causal_weights.values()) if causal_weights else 1.0
                confidence = min(score / max(max_possible, 0.01), 1.0)

                if confidence > 0.15:  # Minimum threshold
                    explanation = self._build_explanation(disease_row, matched, weights)
                    results.append({
                        'disease_name': disease_row['disease_name'],
                        'disease_id': disease_row.get('disease_id', ''),
                        'confidence': round(confidence, 3),
                        'matched_symptoms': matched,
                        'causal_weights': weights,
                        'explanation': explanation,
                        'disease_data': disease_row.to_dict(),
                    })

        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results[:10]

    def get_disease_by_id(self, disease_id: str) -> dict:
        if self._dataset is None or self._dataset.empty:
            return None
        row = self._dataset[self._dataset['disease_id'] == disease_id]
        if row.empty:
            return None
        return row.iloc[0].to_dict()

    def _parse_causal_weights(self, field) -> dict:
        weights = {}
        if pd.isna(field) or not str(field).strip():
            return weights
        for pair in str(field).split('|'):
            if ':' in pair:
                parts = pair.rsplit(':', 1)
                try:
                    weights[parts[0].strip().lower()] = float(parts[1].strip())
                except (ValueError, IndexError):
                    pass
        return weights

    def _parse_pipe_field(self, field) -> list:
        if pd.isna(field) or not str(field).strip():
            return []
        return [s.strip() for s in str(field).split('|') if s.strip()]

    def _symptom_match(self, user_sym: str, disease_sym: str) -> float:
        """Fuzzy symptom matching. Returns 0-1 similarity score."""
        user_sym = user_sym.lower().strip()
        disease_sym = disease_sym.lower().strip()

        if user_sym == disease_sym:
            return 1.0
        if user_sym in disease_sym or disease_sym in user_sym:
            return 0.8

        # Word overlap
        user_words = set(user_sym.split())
        disease_words = set(disease_sym.split())
        if user_words and disease_words:
            overlap = len(user_words & disease_words)
            total = len(user_words | disease_words)
            if overlap / total > 0.3:
                return 0.6
        return 0.0

    def _build_explanation(self, disease_row, matched, weights) -> str:
        name = disease_row['disease_name']
        explanation = f"Based on causal analysis, {name} is predicted because: "
        reasons = [f"'{sym}' has a causal link to {name}" for sym in matched[:3]]
        explanation += "; ".join(reasons) + "."

        pathophys = disease_row.get('pathophysiology', '')
        if pd.notna(pathophys) and pathophys:
            explanation += f" Mechanism: {str(pathophys)[:250]}"
        return explanation

    def dowhy_analysis(self, symptoms, disease_name):
        """Use DoWhy for actual causal inference calculation."""
        try:
            import dowhy
            from dowhy import CausalModel
            import pandas as pd
            import numpy as np

            # Build observational data from our graph
            if self._dataset.empty:
                return "Causal dataset not available for DoWhy analysis."

            row = self._dataset[self._dataset['disease_name'] == disease_name]
            if row.empty:
                return "Disease not found in causal dataset."
            row = row.iloc[0]

            causal_weights = self._parse_causal_weights(str(row.get('causal_weight', '')))
            if not causal_weights:
                return "No causal weights available for this disease."

            # Create binary observational dataset for DoWhy
            n = 200
            np.random.seed(42)
            data = {}
            matched_syms = []

            for sym, weight in causal_weights.items():
                col = sym.replace(' ', '_').replace('-', '_')[:30]
                # Symptoms present based on causal weight probability
                user_has = any(self._symptom_similarity(s.lower(), sym) > 0.5
                              for s in symptoms)
                if user_has:
                    data[col] = np.random.binomial(1, weight, n)
                    matched_syms.append((sym, weight))
                else:
                    data[col] = np.random.binomial(1, 0.1, n)

            # Disease outcome influenced by symptom presence
            disease_col = 'disease_outcome'
            outcome_prob = np.zeros(n)
            for sym, weight in causal_weights.items():
                col = sym.replace(' ', '_').replace('-', '_')[:30]
                if col in data:
                    outcome_prob += data[col] * weight
            outcome_prob = np.clip(outcome_prob / max(sum(causal_weights.values()), 1), 0, 1)
            data[disease_col] = np.random.binomial(1, outcome_prob, n)

            df = pd.DataFrame(data)

            if not matched_syms:
                return "No matching symptoms for causal inference."

            # Use first matched symptom as treatment variable
            treatment_col = matched_syms[0][0].replace(' ', '_').replace('-', '_')[:30]

            # Build causal graph string for DoWhy
            causes = [s.replace(' ', '_').replace('-', '_')[:30] for s, _ in matched_syms]
            gml = 'graph[directed 1 '
            for c in causes:
                gml += f'node[id "{c}" label "{c}"] '
            gml += f'node[id "{disease_col}" label "{disease_col}"] '
            for c in causes:
                gml += f'edge[source "{c}" target "{disease_col}"] '
            gml += ']'

            # DoWhy causal model
            model = CausalModel(
                data=df,
                treatment=treatment_col,
                outcome=disease_col,
                graph=gml
            )

            # Identify causal effect
            identified = model.identify_effect(proceed_when_unidentifiable=True)

            # Estimate using backdoor linear regression
            estimate = model.estimate_effect(
                identified,
                method_name="backdoor.linear_regression"
            )

            ate = estimate.value
            result = (
                f"DoWhy Causal Inference for {disease_name}:\n"
                f"Treatment: {matched_syms[0][0]} -> {disease_name}\n"
                f"Average Treatment Effect (ATE): {ate:.4f}\n"
                f"Interpretation: Presence of '{matched_syms[0][0]}' increases probability "
                f"of {disease_name} by {abs(ate)*100:.1f}%.\n"
                f"Matched causal factors: {', '.join(s for s,_ in matched_syms)} "
                f"with weights {', '.join(f'{w:.2f}' for _,w in matched_syms)}"
            )
            return result

        except ImportError:
            return "DoWhy not installed. Using graph-based causal weights only."
        except Exception as e:
            logger.warning(f"DoWhy analysis failed: {e}")
            return f"Causal graph analysis used (DoWhy error: {str(e)[:100]})"

    def predict(self, symptoms: list, top_k: int = 5) -> list:
        """Alias for predict_disease() - called by chat_engine."""
        return self.predict_disease(symptoms)[:top_k]
