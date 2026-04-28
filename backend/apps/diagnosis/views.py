from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from .serializers import DiseasePredictionSerializer, DiagnosisRequestSerializer
from .models import DiseasePrediction

class DiagnosisView(APIView):
    """Run diagnosis on provided symptoms using Causal AI + RAG."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = DiagnosisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        symptoms = serializer.validated_data['symptoms']

        # Run Causal AI Engine
        from services.causal_engine import CausalEngine
        causal = CausalEngine()
        causal_results = causal.predict_disease(symptoms)

        # Run RAG Engine
        from services.rag_engine import RAGEngine
        rag = RAGEngine()
        rag_results = rag.retrieve_for_symptoms(symptoms)

        return Response({
            'symptoms_analyzed': symptoms,
            'causal_predictions': causal_results[:5],
            'rag_context': [{'content': r['content'][:300], 'score': r['relevance_score']} for r in rag_results[:3]],
        })


class DiseaseInfoView(APIView):
    """Get detailed info about a specific disease from the dataset."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, disease_id):
        from services.causal_engine import CausalEngine
        causal = CausalEngine()
        disease = causal.get_disease_by_id(disease_id)
        if disease is None:
            return Response({'error': 'Disease not found'}, status=404)
        return Response(disease)


class PredictionHistoryView(APIView):
    """Get user's prediction history."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        predictions = DiseasePrediction.objects.filter(user=request.user).order_by('-created_at')[:20]
        serializer = DiseasePredictionSerializer(predictions, many=True)
        return Response(serializer.data)
