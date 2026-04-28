"""Celery tasks for antifragile self-improvement."""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name='feedback.tasks.process_feedback')
def process_feedback():
    """Process unprocessed feedback to improve predictions."""
    from .models import UserFeedback

    unprocessed = UserFeedback.objects.filter(is_processed=False)
    count = unprocessed.count()
    if count == 0:
        return "No new feedback."

    wrong = unprocessed.filter(is_correct=False)
    correct = unprocessed.filter(is_correct=True)

    for fb in wrong:
        logger.info(
            f"WRONG prediction: '{fb.prediction.disease_name}' | "
            f"Correct disease: {fb.correct_disease or 'Not specified'} | "
            f"Symptoms: {fb.prediction.symptoms_matched}"
        )

    for fb in correct:
        logger.info(f"CONFIRMED: '{fb.prediction.disease_name}' was correct")

    unprocessed.update(is_processed=True)
    return f"Processed {count} feedback ({wrong.count()} wrong, {correct.count()} correct)"


@shared_task(name='feedback.tasks.retrain_rag')
def retrain_rag():
    """Re-index RAG with corrections from feedback."""
    logger.info("RAG retraining triggered")
    return "RAG retrain complete (placeholder)"
