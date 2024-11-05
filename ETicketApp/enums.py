from enum import Enum

class TipoRefeicaoEnum(Enum):
    CAFE_DA_MANHA = "CAFE_DA_MANHA"
    ALMOCO = "ALMOCO"
    JANTAR = "JANTAR"

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
    PIX = "PIX"
    DINHEIRO = "DINHEIRO"
    CARTAO = "CARTAO"

    @classmethod
    def choices(cls):
        return [(tag.name, tag.value) for tag in cls]

    @classmethod
    def get_name_by_value(cls, value):
        for item in cls:
            if item.value == value:
                return item.name
        return None