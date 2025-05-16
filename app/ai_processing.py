from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from typing import List, Optional
import logging
import torch

logger = logging.getLogger(__name__)

class FeedbackAnalyzer:
    def __init__(self):
        self.device = 'cpu'
        
        self._load_sentiment_model()
        self._load_labeling_model()
        
    def _load_sentiment_model(self):
        try:
            self.sentiment_model = pipeline(
                "text-classification",
                model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
                device=self.device
            )
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de sentimentos: {e}")
            raise

    def _load_labeling_model(self):
        """Carrega modelo para rotulagem (zero-shot classification)"""
        try:
            self.labeling_model = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
                device=self.device
            )
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de rotulagem: {e}")
            raise

    def analyze_sentiment(self, text: str) -> dict:
        """Analisa o sentimento do texto"""
        try:
            result = self.sentiment_model(text)[0]
            return {
                "score": result["score"],
                "label": result["label"].lower()
            }
        except Exception as e:
            logger.error(f"Erro analisando sentimento: {e}")
            return {"score": 0.0, "label": "neutral"}

    def generate_labels(self, text: str, existing_labels: List[str]) -> List[str]:
        """Gera ou associa rótulos ao texto"""
        try:
            if not existing_labels:
                return []

            # Usa classificação zero-shot para encontrar os rótulos mais relevantes
            result = self.labeling_model(
                text,
                candidate_labels=existing_labels,
                multi_label=True
            )
            
            # Filtra rótulos com score > 0.5
            matched_labels = [
                label for label, score in zip(result['labels'], result['scores'])
                if score > 0.5
            ]
            
            return matched_labels[:3]  # Retorna no máximo 3 rótulos
            
        except Exception as e:
            logger.error(f"Erro gerando rótulos: {e}")
            return []

    def shutdown(self):
        """Libera memória dos modelos"""
        if hasattr(self, 'sentiment_model'):
            del self.sentiment_model
        if hasattr(self, 'labeling_model'):
            del self.labeling_model
        torch.cuda.empty_cache()