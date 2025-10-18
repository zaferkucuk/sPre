"""
Signals for matches application.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Match, Prediction


@receiver(post_save, sender=Match)
def update_predictions_on_match_finish(sender, instance, **kwargs):
    """
    Update prediction correctness when match finishes.
    
    Args:
        sender: Model class
        instance: Match instance
        **kwargs: Additional arguments
    """
    if instance.is_finished and instance.home_score is not None and instance.away_score is not None:
        # Update all predictions for this match
        predictions = Prediction.objects.filter(match=instance, is_correct__isnull=True)
        
        for prediction in predictions:
            # Check if prediction is correct (exact score)
            is_correct = (
                prediction.predicted_home_score == instance.home_score and
                prediction.predicted_away_score == instance.away_score
            )
            
            prediction.is_correct = is_correct
            prediction.save(update_fields=['is_correct'])
