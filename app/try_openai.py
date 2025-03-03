import openai

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

models = openai.Model.list()

print([model["id"] for model in models["data"]])
