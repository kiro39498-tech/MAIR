from config.settings import settings
from openai import AzureOpenAI

versions = ['2024-10-21','2024-08-01-preview','2024-02-01','2024-05-01-preview','2024-06-01','2024-07-01-preview','2025-03-01-preview','preview']
for version in versions:
    client = AzureOpenAI(api_key=settings.azure_openai_api_key, api_version=version, azure_endpoint=settings.azure_openai_endpoint)
    try:
        resp = client.responses.create(model=settings.azure_openai_deployment, input='hi')
        print('VERSION', version, 'OK', getattr(resp, 'output_text', None))
    except Exception as e:
        print('VERSION', version, 'ERR', type(e).__name__, e)
