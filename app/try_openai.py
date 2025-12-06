import openai

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config.settings import settings

openai.api_key = settings.OPENAI_API_KEY

models = openai.Model.list()

print([model["id"] for model in models["data"]])
