from openai import OpenAI
import os, requests


def inference(
    system_prompt: str,
    prompt: str,
    protocol: str = "http",
    ip: str = "localhost",
    port: int = 8001,
    temperature: float = 0.1,
    top_p: float = 0.9,
    max_completion_tokens: int = 2048,
    model_name: str = "qwen-14b",
) -> str | None:
    addr = f"{protocol}://{ip}:{port}/v1"
    client = OpenAI(api_key="dummy", base_url=addr)
    
    prompt = f"""TEXT TO ANALYZE:
                 {prompt}
                 DON'T FORGET ABOUT RULES ABOVE!
              """

    messages = [
        
        {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    ]

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_completion_tokens=max_completion_tokens,
        )
        return response.choices[0].message.content

    except requests.exceptions.ConnectionError:
        print(f"Не удалось подключиться к {addr}")
    except Exception as e:
        print(f"Ошибка при запросе: {e}")
    return None


if __name__ == "__main__":
    system_prompt = """"
                    Extract ONLY arable land and pasture data from the text:

                    KEYWORDS TO FIND:
                    - Пашня/егістік → arable_land
                    - Пастбища/Шабындық → pastures

                    RULES:
                    1. Search for these keywords only (case-insensitive)
                    2. Extract area values in hectares (га/гектар)
                    3. If multiple values found for same type → collect in array
                    4. Ignore all other land types
                    5. Return ONLY valid JSON, no explanations

                    OUTPUT FORMAT:
                    {
                    "arable_land": ["value1", "value2"] or "single value" or null,
                    "pastures": ["value1", "value2"] or "single value" or null
                    }

                    EXAMPLES:
                    Input: "Пашня 18 га, егістік 25 гектар, Пастбища 200 га"
                    Output: {"arable_land": ["18 га", "25 га"], "pastures": "200 га"}

                    Input: "Сенокос 50 га, Пашня 18 га, дорога 10 га"
                    Output: {"arable_land": "18 га", "pastures": null}
    """
    
    with open("qwen/prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read().strip()
    
    result = inference(system_prompt, prompt)
    print(result)
