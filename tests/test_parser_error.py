from typing import Annotated

from pytest import raises

from xdsl.ir import MLContext
from xdsl.irdl import (
    AnyAttr,
    irdl_op_definition,
    IRDLOperation,
    VarOperand,
    VarOpResult,
)
from xdsl.parser import Parser
from xdsl.utils.exceptions import ParseError


@irdl_op_definition
class UnkownOp(IRDLOperation):
    name = "unknown"
    ops: Annotated[VarOperand, AnyAttr()]
    res: Annotated[VarOpResult, AnyAttr()]


def check_error(prog: str, line: int, column: int, message: str):
    ctx = MLContext()
    ctx.register_op(UnkownOp)

    parser = Parser(ctx, prog)
    with raises(ParseError) as e:
        parser.parse_operation()

    assert e.value.span

    assert e.value.history is not None

    for err in e.value.history.iterate():
        if message in err.error.msg:
            assert err.error.span.get_line_col() == (line, column)
            break
    else:
        assert False, "'{}' not found in an error message {}!".format(
            message, e.value.args
        )


def test_parser_missing_equal():
    """Test a missing equal sign error."""
    ctx = MLContext()
    ctx.register_op(UnkownOp)

    prog = """
"unknown"() ({
  %0 "unknown"() : () -> !i32
}) : () -> ()
"""
    check_error(prog, 3, 5, "Operation definitions expect an `=` after op-result-list!")


def test_parser_redefined_value():
    """Test an SSA value redefinition error."""
    ctx = MLContext()
    ctx.register_op(UnkownOp)

    prog = """
"unknown"() ({
  %val = "unknown"() : () -> i32
  %val = "unknown"() : () -> i32
}) : () -> ()
"""
    check_error(prog, 4, 2, "SSA value %val is already defined")


def test_parser_missing_operation_name():
    """Test a missing operation name error."""
    ctx = MLContext()
    ctx.register_op(UnkownOp)

    prog = """
"unknown"() ({
  %val =
}) : () -> ()
"""
    check_error(prog, 4, 0, "Expected an operation name here")
