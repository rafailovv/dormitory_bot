from transliterate import translit

def validate_block(block: str):
    """ Проверяем блок на валидность """
    block = block.strip()
    if len(block) != 4:
        return False

    block = block.upper()
    block = translit(block, "ru")
    
    if block[-1] not in "АБВГ":
        return False

    if block[0].isdecimal() and block[1].isdecimal() and block[2].isdecimal() and block[-1].isalpha() and 200 < int(block[0:-1]) < 941: # Проверка на самый максимальный блок
        return block
    return False

def validate_car(car_mark: str, cars_marks_base: list):
    """ Проверяем марку машины на валидность """
    car_mark = car_mark.strip().lower()

    for car in cars_marks_base:
        if car["name"].lower() == car_mark:
            return True
    
    return False