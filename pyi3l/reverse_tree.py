import ast
from dataclasses import is_dataclass
from itertools import takewhile, dropwhile
from typing import Union, get_origin, get_args

def astize(o):
	if isinstance(o, float) or isinstance(o, int) or isinstance(o, str) or o is None:
		return ast.Constant(o)
	if isinstance(o, list):
		return ast.List(elts=[astize(i) for i in o])
	if isinstance(o, dict):
		return ast.Dict(
			keys=[astize(i) for i in o.keys()],
			values=[astize(i) for i in o.values()],
		)
	elif is_dataclass(o):
		return astize_dataclass(o)
	else:
		raise ValueError(f"unsupported {o}")

def is_optional_type(t):
	return get_origin(t) is Union and type(None) in get_args(t)

def suitable_for_positional_arg(kv):
	f = kv[1]
	return not is_optional_type(f.type)

def split_args(o):
	fields = o.__dataclass_fields__.items()
	if len(fields) == 1:
		args = fields
		kwargs = []
	else:
		args = list(takewhile(suitable_for_positional_arg, fields))
		kwargs = list(dropwhile(suitable_for_positional_arg, fields))
	return args, kwargs

def astize_dataclass(o):
	args, kwargs = split_args(o)
	return ast.Call(
		func=ast.Name(id=o.__class__.__name__),
		args=[
			astize(getattr(o, k))
			for k, v in args
		],
		keywords=[
			ast.keyword(
				arg=k,
				value=astize(getattr(o, k))
			)
			for k, v in kwargs
			if v.default != getattr(o, k)
		],
	)

def pythonize(o):
	return ast.unparse(astize(o))

def pythonize_full(o):
	return "#!/usr/bin/python\n" + ast.unparse(
		ast.Module(
			body=[
				ast.ImportFrom(
					module='pyi3l',
					names=[ast.alias(name='*')],
				),
				ast.ImportFrom(
					module='pyi3l.cmd',
					names=[ast.alias(name='apply')],
				),
				ast.Expr(
					ast.Call(
						func=ast.Name(id='apply'),
						args=[astize(o)],
						keywords=[],
					)
				)

			],
			type_ignores=[],
		)
	)
