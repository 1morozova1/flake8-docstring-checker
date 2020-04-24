from functools import wraps
from operator import itemgetter, attrgetter
from pathlib import Path
from ast import Module
from .docstring_detection import get_object_info, ReturnState, ObjectInfo
from typing import NamedTuple, Optional, Callable, Tuple, List
from docstring_parser import parse
from docstring_parser.common import Docstring


class _Error(NamedTuple):
	code: str
	message: str
	line: int
	column: int


class DocstringInfo(NamedTuple):
	first_line: str
	args_lines: str
	returns_lines: str
	multiline: bool


ERRORS_STRUCTURE = Optional[Tuple[str, str, ObjectInfo]]

errors: List[_Error] = []

quotes = '\'\'\''


def _add_error(func: Callable):
	@wraps(func)
	def _func_wrapper(*args, **kwargs):
		res = func(*args, **kwargs)
		if res:
			code, message, data = res
			row, col = data.position
			errors.append(_Error(code, message, row, col))
		return res
	return _func_wrapper


def get_file_content(filepath: Path) -> str:
	with open(str(filepath), 'r') as f:
		file_content = f.read()
	return file_content


class DocstringsChecker:
	'''Обрабатывает ошибки в докстрингах.'''
	name = __name__
	version = 0.1

	# noinspection PyUnusedLocal
	def __init__(self, tree: Module, filename) -> None:
		self._filepath = Path(filename)

	def run(self):
		'''Вывод найденных ошибок в консоль.'''
		if self._filepath.name.startswith('test_'):
			return
		self.get_docstring_errors()
		for error in errors:
			message = f'{error.code} {error.message}'
			yield (error.line, error.column, message, type(self))
		errors.clear()

	@_add_error
	def check_docstring_exist(
		self, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка наличия докстринга.

		Args:
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if cur_data.docs:
			return None
		return (
			'D101/D102/D103',
			'Missing docstring in public class/method/function.',
			cur_data
		)

	@_add_error
	def triple_single_quotes_check(
		self, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка на тройные одинарные кавычки.

		Args:
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if cur_data.docs.startswith(quotes) and cur_data.docs.endswith(quotes):
			return None
		return 'D300', 'Use triple single quotes.', cur_data

	@_add_error
	def multiline_closing_quotes_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка закрывающихся кавычек на отдельной строке.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if not docs_info.blank_after_short_description:
			return None
		elif cur_data.docs[-3:] == quotes:
			return None
		return (
			'D209', 'Multi-line docstring closing quotes '
			'should be on a separate line.', cur_data)

	@_add_error
	def first_line_capital_letter_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка начала первой строки с большой буквы.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if docs_info.short_description[3].isupper():
			return None
		return (
			'D212', 'Docstring summary should start at '
			'the first line with a capital letter.',
			cur_data
		)

	@_add_error
	def first_line_period_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка окончания первой строки точкой.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if docs_info.short_description.strip("'").endswith('.'):
			return None
		return (
			'D400', 'First line should end with a period.',
			cur_data
		)

	@_add_error
	def blank_line_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка отступа между первой строкой и описанием.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if docs_info.blank_after_short_description or docs_info.short_description.endswith(quotes):
			return None
		return (
			'D205', '1 blank (maybe you should remove whitespaces) line '
			'required between summary line and description.', cur_data)

	@_add_error
	def have_function_args_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка есть ли Args при необходимости.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if not cur_data.args or docs_info.params:
			return None
		return (
			'D405',
			'Args: should be implemented, during function have arguments.',
			cur_data)

	@_add_error
	def args_list_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка все ли аргументы перечислены в докстринге.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if not docs_info.params:
			return None
		docs_params = tuple(map(attrgetter('arg_name'), docs_info.params))
		if docs_params == tuple((map(itemgetter(0), cur_data.args))):
			return None
		return 'D406', 'Argument wasn`t implemented in args list.', cur_data

	@_add_error
	def argument_annotation_check(
		self, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка аннотаций у аргументов.

		Args:
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if not cur_data.args or all(map(itemgetter(1), cur_data.args)):
			return None
		return 'D411', 'Arguments must be annotated', cur_data

	@_add_error
	def have_function_return_check(
		self, docs_info: Docstring, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка есть ли Returns при необходимости.

		Args:
			docs_info: Объекты докстринга.
			cur_data: Объекты проверяемого метода/класса..

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if docs_info.returns or cur_data.returns != ReturnState.ANY:
			return None
		return (
			'D407', '"Returns:" should be implemented, '
			'during function returns something.', cur_data)

	@_add_error
	def check_operator(
		self, cur_data: ObjectInfo) -> ERRORS_STRUCTURE:
		'''Проверка оператора ->.

		Args:
			cur_data: Объекты проверяемого метода/класса.

		Returns:
			Код, сообщение, строка, колонка ошибки, если ошибка. Иначе ничего.
		'''
		if cur_data.returns != ReturnState.ERROR:
			return None
		return 'D410', 'Operator -> should be implemented', cur_data

	def get_docstring_errors(self) -> None:
		'''Получение ошибок.'''
		_file_content = get_file_content(self._filepath)
		data = get_object_info(_file_content)
		for cur_data in data:
			if cur_data.name.startswith('_') and not cur_data.docs:
				continue
			self.check_operator(cur_data)
			self.check_docstring_exist(cur_data)
			if not cur_data.docs:
				continue
			docstring_info = parse(cur_data.docs)
			self.triple_single_quotes_check(cur_data)
			self.multiline_closing_quotes_check(docstring_info, cur_data)
			self.first_line_capital_letter_check(docstring_info, cur_data)
			self.first_line_period_check(docstring_info, cur_data)
			self.blank_line_check(docstring_info, cur_data)
			if cur_data.is_class:
				continue
			self.have_function_args_check(docstring_info, cur_data)
			self.args_list_check(docstring_info, cur_data)
			self.argument_annotation_check(cur_data)
			self.have_function_return_check(docstring_info, cur_data)
