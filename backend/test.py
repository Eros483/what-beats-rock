from openai import OpenAI

openai_api_key ="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"
client=OpenAI(api_key=openai_api_key)
response=client.responses.create(
    model="gpt-3.5-turbo",
    input="What beats rock",
    temperature=0,
    )
print(response.output_text)