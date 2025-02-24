"""OpenAI Pricing.

This module contains pricing information for various OpenAI embedding models.
"""

# Price per token in $ for the OpenAI embeddings
OPENAI_EMBEDDINGS_PRICING = {
    "text-embedding-3-small": 0.02 / 1000000,
    "text-embedding-3-large": 0.13 / 1000000,
    "text-embedding-ada-002": 0.10 / 1000000,
}
