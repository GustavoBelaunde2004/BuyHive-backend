import openai

openai.api_key = "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"

models = openai.Model.list()
print([model["id"] for model in models["data"]])
