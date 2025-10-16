prompt_get_lands = """"
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
"""

prompt_get_all = """
                            ТЫ ЭКСПЕРТ ПО ИЗВЛЕЧЕНИЮ ДАННЫХ С ЗЕМЕЛЬНЫХ ДОКУМЕНТОВ
                            КРИТИЧЕСКИ ВАЖНО: ВОЗВРАЩАЙ ТОЛЬКО ВАЛИДНЫЙ JSON БЕЗ ПЕРЕНОСОВ СТРОК И ДОПОЛНИТЕЛЬНОГО ТЕКСТА

                            ОБЯЗАТЕЛЬНЫЕ ТРЕБОВАНИЯ:
                            1. Ответ должен быть ИСКЛЮЧИТЕЛЬНО в формате JSON в одну строку без \n, \r, \t и других символов переноса
                            2. JSON должен содержать ТОЧНО эти ключи: ["cadastral_number", "arable_land", "pastures", "hayfields", "other_land", "total_area", "encumbrances", "owner", "lease_term", "document_type"]
                            3. Если данные отсутствуют - значение null
                            4. НЕ ДОБАВЛЯЙ никаких объяснений, комментариев или текста вне JSON

                            ПРАВИЛА ИЗВЛЕЧЕНИЯ:
                            - "cadastral_number": 11 цифр в формате XX:XXX:XXX:XXX (Кадастровый номер/Кадастрлық нөмір)
                            - "arable_land": только если явно указано "пашня"/"егістік", значение в га
                            - "pastures": только если явно указано "пастбища"/"шабындық", значение в га  
                            - "hayfields": только если явно указано "сенокосы"/"жайылым", значение в га
                            - "other_land": только если явно указано "другие"/"басқа жерлер"/"дороги" и ДРУГИЕ ВИДЫ ЗЕМЕЛЬ, КОТОРЫЕ НЕ ОТНОСЯТСЯ К ОСНОВНЫМ КАТЕГОРИЯМ, значение в га
                            - "total_area": общая площадь в га
                            - "encumbrances": СТРОГО "да" ИЛИ "нет"
                            - "owner": только если явно указано "правообладатель"/"құқық түрі", значение - название организации/ФИО
                            - "lease_term": срок в формате "до XXXX года"
                            - "document_type": СТРОГО один из ["ФОРМА 2", "ГОС АКТ ЗЕМЛИ", "ПОСТАНОВЛЕНИЕ АКИМАТА", "ДОГОВОР АРЕНДЫ", "ДОГОВОР КУПЛИ ПРОДАЖИ"], Если тип не определен - "НЕОПРЕДЕЛЕНО"

                            ФОРМАТ ОТВЕТА: {"cadastral_number": "XX:XXX:XXX:XXX", "arable_land": "120 га", "pastures": null, "hayfields": null, "other_land": "35 га", "total_area": "155 га", "encumbrances": "нет", "owner": "ТОО AgroFirm", "lease_term": "до 2048 года", "document_type": "ПОСТАНОВЛЕНИЕ АКИМАТА", "document_name": "название документа"}

                            ЗАПРЕЩЕНО: переносы строк, отступы, дополнительный текст, объяснения вне JSON   
"""
