from enum import Enum

class TipoRefeicaoEnum(Enum):
    CAFE_DA_MANHA = 1
    ALMOCO = 2
    JANTAR = 3

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]
    
    @classmethod
    def get_name_by_value(cls, value):
        for item in cls:
            if item.value == value:
                return item.name
        return None

class MetodoPagamentoEnum(Enum):
    PIX = 1
    DINHEIRO = 2
    CARTAO = 3

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

    @classmethod
    def get_name_by_value(cls, value):
        for item in cls:
            if item.value == value:
                return item.name
        return None