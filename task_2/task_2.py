"""
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с
информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными. Для
этого:
a. Создать функцию write_order_to_json(), в которую передается 5 параметров — товар
(item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция
должна предусматривать запись данных в виде словаря в файл orders.json. При
записи данных указать величину отступа в 4 пробельных символа;
b. Проверить работу программы через вызов функции write_order_to_json() с передачей
в нее значений каждого параметра.
"""
import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('task_2/orders.json') as file_obj:
        content = json.load(file_obj)

    order = {
        "item": item,
        "quantity": quantity,
        "price": price,
        "buyer": buyer,
        "date": date
    }
    content['orders'].append(order)
    with open('task_2/orders.json', 'w') as file_obj:
        json.dump(content, file_obj, indent=4, ensure_ascii=False)


test_list = [
    ['item1', 1, 100.00, 'buyer1', '01.01.2022'],
    ['предмет2', 1, 100.00, 'покупатель2', '01.01.2022'],
]
for item in test_list:
    write_order_to_json(*item)
