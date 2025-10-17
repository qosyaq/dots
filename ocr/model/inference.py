import requests
from ocr.utils.image_utils import PILimage_to_base64
from openai import OpenAI
import os


def inference_with_vllm(
    image,
    prompt,
    protocol="http",
    ip="localhost",
    port=8000,
    temperature=0.1,
    top_p=0.9,
    max_completion_tokens=32768,
    model_name="rednote-hilab/dots.ocr",
):

    addr = f"{protocol}://{ip}:{port}/v1"
    client = OpenAI(api_key="{}".format(os.environ.get("API_KEY", "0")), base_url=addr)
    messages = []
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": PILimage_to_base64(image)},
                },
                {
                    "type": "text",
                    "text": f"<|img|><|imgpad|><|endofimg|>{prompt}",
                },  # if no "<|img|><|imgpad|><|endofimg|>" here,vllm v1 will add "\n" here
            ],
        }
    )
    try:
        response = client.chat.completions.create(
            messages=messages,
            model=model_name,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            top_p=top_p,
            extra_body={"repetition_penalty": 1.2},
        )
        response = response.choices[0].message.content
        return response
    except requests.exceptions.RequestException as e:
        print(f"request error: {e}")
        return None
