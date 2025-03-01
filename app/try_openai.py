import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

models = openai.Model.list()
print([model["id"] for model in models["data"]])
