from pyparsing import *

COMMENT = Regex(r"/\-(?:[^-]|\-(?!/))*\-\/").set_name("comment")

IDENT = unicode_set.identifier()

DEF, EXAMPLE, INDUCTIVE, OPEN, TYPE = map(
    lambda w: Suppress(Keyword(w)), "def example inductive open Type".split()
)

ASSIGN, ARROW, FUN, TO = map(
    lambda s: Suppress(s[0]) | Suppress(s[1:]), "≔:= →-> λfun ↦=>".split()
)

LPAREN, RPAREN, LBRACE, RBRACE, COLON, UNDER, BAR = map(Suppress, "(){}:_|")
inline_one_or_more = lambda e: OneOrMore(Opt(Suppress(White(" \t\r"))) + e)

expr, fn_type, fn, call, i_arg, e_arg, p_expr, type_, ph, ref = map(
    lambda n: Forward().set_name(n),
    "expr fn_type fn call implicit_arg explicit_arg paren_expr type placeholder ref".split(),
)

expr <<= fn_type | fn | call | p_expr | type_ | ph | ref

name = Group(IDENT).set_name("name")
i_param = (LBRACE + name + COLON + expr + RBRACE).set_name("implicit_param")
e_param = (LPAREN + name + COLON + expr + RPAREN).set_name("explicit_param")
fn_type <<= (i_param | e_param) + ARROW + expr
fn <<= FUN + Group(OneOrMore(name)) + TO + expr
callee = ref | p_expr
call <<= (callee + inline_one_or_more(i_arg | e_arg)).leave_whitespace()
i_arg <<= LPAREN + IDENT + ASSIGN + expr + RPAREN
e_arg <<= (type_ | ref | p_expr).leave_whitespace()
p_expr <<= LPAREN + expr + RPAREN
type_ <<= Group(TYPE)
ph <<= Group(UNDER)
ref <<= Group(name)

return_type = Opt(COLON + expr)
params = Group(ZeroOrMore(i_param | e_param))
definition = (DEF + ref + params + return_type + ASSIGN + expr).set_name("definition")
example = (EXAMPLE + params + return_type + ASSIGN + expr).set_name("example")
constraint = i_arg.copy()
ctor = BAR + name + Group(ZeroOrMore(i_param | e_param)) + ZeroOrMore(constraint)
data = (
    (INDUCTIVE + IDENT + Group(ZeroOrMore(ctor)) + OPEN + IDENT)
    .add_condition(lambda r: r[0] == r[2], message="open and datatype name mismatch")
    .set_name("datatype")
)
declaration = (definition | example | data).set_name("declaration")

program = ZeroOrMore(declaration).ignore(COMMENT).set_name("program")

line_exact = lambda w: Suppress(AtLineStart(w) + LineEnd())
markdown = line_exact("```lean") + program + line_exact("```")
