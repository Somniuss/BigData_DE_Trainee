import json
import xml.etree.ElementTree as ET
import decimal  # добавляем

# Новый класс для работы с Decimal
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return float(obj)  # конвертируем Decimal в float
        return super().default(obj)


class Exporter:
    @staticmethod
    def to_json(data):
        # передаем DecimalEncoder в json.dumps
        return json.dumps(data, indent=4, ensure_ascii=False, cls=DecimalEncoder)

    @staticmethod
    def to_xml(data, root_name="data", item_name="item"):
        root = ET.Element(root_name)
        for row in data:
            item = ET.SubElement(root, item_name)
            for key, value in row.items():
                child = ET.SubElement(item, key)
                child.text = str(value)
        return ET.tostring(root, encoding="utf-8").decode()
