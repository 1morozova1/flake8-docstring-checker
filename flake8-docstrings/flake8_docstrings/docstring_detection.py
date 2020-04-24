# coding=utf-8
from parso import parse
from parso.python.tree import Class, Function, Module, Keyword, Name
from typing import List, Union, Tuple, Optional
from dataclasses import dataclass


class ReturnState:
    '''Тип возвращаемого функцией.

    0 - Отсутствует оператор -> в функции
    1 - Возвращает None
    2 - Возвращает что-либо отличное от None
    '''
    ERROR = 0
    NONE = 1
    ANY = 2


@dataclass
class ObjectInfo:
    '''NamedTuple для параметров класса/функции.'''
    is_class: bool
    position: Tuple[int, int]
    name: str
    docs: Optional[str]
    args: Optional[Tuple[str]] = None
    returns: int = ReturnState.NONE


_data: List[ObjectInfo] = []


def _parse_returns(func: Function) -> int:
    '''Парсит, что возвращает функция.

    Args:
        func: Проверяемая фукнция.

    Returns:
        Одно из значений, что возращает функция.
    '''
    returns_annotat = func.annotation
    if func.children[3] != '->':
        return ReturnState.ERROR
    if isinstance(returns_annotat, Keyword) and returns_annotat.value == 'None':
        return ReturnState.NONE
    return ReturnState.ANY


def _parse_args(func: Function) -> Tuple[Tuple[str, Optional[Name]], ...]:
    '''Парсит аргументы фукнции.

    Args:
        func: Проверяемая функция.

    Returns:
        Tuple из имен аргументов и их аннотаций.
    '''

    def _get_arg(param):
        return param.name.value not in ('self', 'cls', '*args', '**kwargs')

    def _get_name_and_annotation(elem):
        return elem.name.value, elem.annotation

    params = filter(_get_arg, func.get_params())
    return tuple(map(_get_name_and_annotation, params))


def _parse_docs(parso_object: Union[Class, Function]) -> Optional[str]:
    '''Парсит докстринг функции/класса.

    Args:
        parso_object: Проверяемый объект.

    Returns:
        Докстринг.
    '''
    docs_node = parso_object.get_doc_node()
    if not docs_node:
        return None
    return docs_node.value


def _parse_data(parso_object: Union[Class, Function]) -> ObjectInfo:
    '''Парсит класс/фукнцию.

    Args:
        parso_object: Проверяемый объект.

    Returns:
        NamedTuple с параметрами функции/класса.
    '''
    fields = {
        'name': parso_object.name.value,
        'docs': _parse_docs(parso_object),
        'position': parso_object.start_pos,
        'is_class': isinstance(parso_object, Class),
    }
    if isinstance(parso_object, Function):
        fields['args'] = _parse_args(parso_object)
        fields['returns'] = _parse_returns(parso_object)
    return ObjectInfo(**fields)


def _walk(current_node: Union[Module, Class, Function]) -> None:
    '''Вызывает парсеры класса и функции.

    Args:
        current_node: текущий объект в проверяемом файле.
    '''
    if type(current_node) in (Function, Class):
        _data.append(_parse_data(current_node))
    for cur in current_node.iter_classdefs():
        _walk(cur)
    for cur in current_node.iter_funcdefs():
        _walk(cur)


def get_object_info(file_content: str) -> List[ObjectInfo]:
    '''Парсер файла для докстрингов.

    Args:
        file_content: содержимое файла.

    Returns:
        Объекты описания классов / функций исходного файла.
    '''
    _data.clear()
    _walk(parse(file_content))
    return _data
