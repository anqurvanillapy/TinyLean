from unittest import TestCase

from . import parse
from .. import ast, Name, grammar, Param, Decl


class TestParser(TestCase):
    def test_fresh(self):
        self.assertNotEqual(Name("i").id, Name("j").id)

    def test_parse_name(self):
        x = parse(grammar.name, "  hello")[0]
        assert isinstance(x, Name)
        self.assertEqual("hello", x.text)

    def test_parse_name_unbound(self):
        x = parse(grammar.name, "_")[0]
        self.assertTrue(x.is_unbound())

    def test_parse_type(self):
        x = parse(grammar.type_, "  Type")[0]
        assert isinstance(x, ast.Type)
        self.assertEqual(2, x.loc)

    def test_parse_reference(self):
        x = parse(grammar.ref, "  hello")[0]
        assert isinstance(x, ast.Ref)
        self.assertEqual(2, x.loc)
        self.assertEqual("hello", x.name.text)

    def test_parse_paren_expr(self):
        x = parse(grammar.p_expr, "(hello)")[0]
        assert isinstance(x, ast.Ref)
        self.assertEqual(1, x.loc)
        self.assertEqual("hello", x.name.text)

    def test_parse_implicit_param(self):
        x = parse(grammar.implicit_param, " {a: b}")[0]
        assert isinstance(x, Param)
        self.assertTrue(x.implicit)
        self.assertEqual("a", x.name.text)
        assert isinstance(x.type, ast.Ref)
        self.assertEqual(5, x.type.loc)

    def test_parse_explicit_param(self):
        x = parse(grammar.explicit_param, " (a : Type)")[0]
        assert isinstance(x, Param)
        self.assertFalse(x.implicit)
        self.assertEqual("a", x.name.text)
        assert isinstance(x.type, ast.Type)
        self.assertEqual(6, x.type.loc)

    def test_parse_call(self):
        x = parse(grammar.call, "a b")[0]
        assert isinstance(x, ast.Call)
        self.assertEqual(0, x.loc)
        assert isinstance(x.callee, ast.Ref)
        self.assertEqual(0, x.callee.loc)
        self.assertEqual("a", x.callee.name.text)
        self.assertEqual(2, x.arg.loc)
        assert isinstance(x.arg, ast.Ref)
        self.assertEqual("b", x.arg.name.text)

    def test_parse_call_paren(self):
        x = parse(grammar.call, "(a) b (Type)")[0]
        assert isinstance(x, ast.Call)
        self.assertEqual(0, x.loc)
        assert isinstance(x.callee, ast.Call)
        assert isinstance(x.callee.callee, ast.Ref)
        self.assertEqual(1, x.callee.callee.loc)
        self.assertEqual("a", x.callee.callee.name.text)
        assert isinstance(x.callee.arg, ast.Ref)
        self.assertEqual(4, x.callee.arg.loc)
        self.assertEqual("b", x.callee.arg.name.text)
        assert isinstance(x.arg, ast.Type)
        self.assertEqual(7, x.arg.loc)

    def test_parse_call_paren_function(self):
        x = parse(grammar.call, "(fun _ => Type) Type")[0]
        assert isinstance(x, ast.Call)
        self.assertEqual(0, x.loc)
        assert isinstance(x.callee, ast.Fn)
        self.assertEqual(1, x.callee.loc)
        self.assertTrue(x.callee.param.is_unbound())
        assert isinstance(x.callee.body, ast.Type)
        self.assertEqual(10, x.callee.body.loc)
        assert isinstance(x.arg, ast.Type)
        self.assertEqual(16, x.arg.loc)

    def test_parse_function_type(self):
        x = parse(grammar.fn_type, "  (a : Type) -> a")[0]
        assert isinstance(x, ast.FnType)
        assert isinstance(x.param, Param)
        self.assertEqual("a", x.param.name.text)
        assert isinstance(x.param.type, ast.Type)
        self.assertEqual(7, x.param.type.loc)
        assert isinstance(x.ret, ast.Ref)
        self.assertEqual("a", x.ret.name.text)
        self.assertEqual(16, x.ret.loc)

    def test_parse_function_type_long(self):
        x = parse(grammar.fn_type, " {a : Type} -> (b: Type) -> a")[0]
        assert isinstance(x, ast.FnType)
        assert isinstance(x.param, Param)
        self.assertEqual("a", x.param.name.text)
        assert isinstance(x.param.type, ast.Type)
        self.assertEqual(6, x.param.type.loc)
        assert isinstance(x.ret, ast.FnType)
        assert isinstance(x.ret.param, Param)
        self.assertEqual("b", x.ret.param.name.text)
        assert isinstance(x.ret.param.type, ast.Type)
        self.assertEqual(19, x.ret.param.type.loc)
        assert isinstance(x.ret.ret, ast.Ref)
        self.assertEqual("a", x.ret.ret.name.text)
        self.assertEqual(28, x.ret.ret.loc)

    def test_parse_function(self):
        x = parse(grammar.fn, "  fun a => a")[0]
        assert isinstance(x, ast.Fn)
        self.assertEqual(2, x.loc)
        assert isinstance(x.param, Name)
        self.assertEqual("a", x.param.text)
        assert isinstance(x.body, ast.Ref)
        self.assertEqual("a", x.body.name.text)
        self.assertEqual(11, x.body.loc)

    def test_parse_function_long(self):
        x = parse(grammar.fn, "   fun a => fun b => a b")[0]
        assert isinstance(x, ast.Fn)
        self.assertEqual(3, x.loc)
        assert isinstance(x.param, Name)
        self.assertEqual("a", x.param.text)
        assert isinstance(x.body, ast.Fn)
        self.assertEqual(12, x.body.loc)
        assert isinstance(x.body.param, Name)
        self.assertEqual("b", x.body.param.text)
        assert isinstance(x.body.body, ast.Call)
        self.assertEqual(21, x.body.body.loc)
        assert isinstance(x.body.body.callee, ast.Ref)
        self.assertEqual("a", x.body.body.callee.name.text)
        assert isinstance(x.body.body.arg, ast.Ref)
        self.assertEqual("b", x.body.body.arg.name.text)

    def test_parse_function_multi(self):
        x = parse(grammar.fn, "  fun c d => c d")[0]
        assert isinstance(x, ast.Fn)
        self.assertEqual(2, x.loc)
        assert isinstance(x.param, Name)
        self.assertEqual("c", x.param.text)
        assert isinstance(x.body, ast.Fn)
        self.assertEqual(2, x.body.loc)
        assert isinstance(x.body.param, Name)
        self.assertEqual("d", x.body.param.text)

    def test_parse_definition_constant(self):
        x = parse(grammar.definition, "  def f : Type := Type")[0]
        assert isinstance(x, Decl)
        self.assertEqual(6, x.loc)
        self.assertEqual("f", x.name.text)
        self.assertEqual(0, len(x.params))
        assert isinstance(x.ret, ast.Type)
        self.assertEqual(10, x.ret.loc)
        assert isinstance(x.body, ast.Type)
        self.assertEqual(18, x.body.loc)

    def test_parse_definition(self):
        x = parse(grammar.definition, "  def f {a: Type} (b: Type): Type := a")[0]
        assert isinstance(x, Decl)
        self.assertEqual(6, x.loc)
        self.assertEqual("f", x.name.text)
        assert isinstance(x.params, list)
        self.assertEqual(2, len(x.params))
        assert isinstance(x.params[0], ast.Param)
        self.assertTrue(x.params[0].implicit)
        self.assertEqual("a", x.params[0].name.text)
        assert isinstance(x.params[0].type, ast.Type)
        self.assertEqual(12, x.params[0].type.loc)
        assert isinstance(x.params[1], ast.Param)
        self.assertFalse(x.params[1].implicit)
        self.assertEqual("b", x.params[1].name.text)
        assert isinstance(x.params[1].type, ast.Type)
        self.assertEqual(22, x.params[1].type.loc)

    def test_parse_program(self):
        x = list(
            parse(
                grammar.program,
                """
                def a: Type := Type
                def b: Type := Type
                """,
            )
        )
        self.assertEqual(2, len(x))
        assert isinstance(x[0], Decl)
        self.assertEqual("a", x[0].name.text)
        assert isinstance(x[1], Decl)
        self.assertEqual("b", x[1].name.text)

    def test_parse_example(self):
        x = parse(grammar.example, "  example: Type := Type")[0]
        assert isinstance(x, Decl)
        self.assertEqual(2, x.loc)
        self.assertTrue(x.name.is_unbound())
        self.assertEqual(0, len(x.params))
        assert isinstance(x.ret, ast.Type)
        assert isinstance(x.body, ast.Type)

    def test_parse_placeholder(self):
        x = parse(grammar.fn, " fun _ => _")[0]
        assert isinstance(x, ast.Fn)
        self.assertTrue(x.param.is_unbound())
        assert isinstance(x.body, ast.Placeholder)
        self.assertEqual(10, x.body.loc)

    def test_parse_return_type(self):
        x = parse(grammar.return_type, ": Type")[0]
        assert isinstance(x, ast.Type)
        self.assertEqual(2, x.loc)

    def test_parse_return_placeholder(self):
        x = parse(grammar.return_type, "")[0]
        assert isinstance(x, ast.Placeholder)
        self.assertFalse(x.is_user)

    def test_parse_definition_no_return(self):
        x = parse(grammar.definition, "def a := Type")[0]
        assert isinstance(x.ret, ast.Placeholder)
        self.assertFalse(x.ret.is_user)

    def test_parse_call_implicit(self):
        x = parse(grammar.call, "a ( T := Nat )")[0]
        assert isinstance(x, ast.Call)
        assert isinstance(x.callee, ast.Ref)
        self.assertEqual("a", x.callee.name.text)
        assert isinstance(x.implicit_to, str)
        self.assertEqual("T", x.implicit_to)
        assert isinstance(x.arg, ast.Ref)
        self.assertEqual("Nat", x.arg.name.text)
