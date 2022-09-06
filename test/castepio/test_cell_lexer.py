from castepio import cell


def test_lex1():
    source1 = open("test/resources/c_dia_p010.cell").read()
    tokens1 = cell.CellLexer.static_lex(source1)
    source2 = cell.CellLexer.tokpass(source1)
    tokens2 = cell.CellLexer.static_lex(source2)
    types1 = [token.token_type for token in tokens1]
    types2 = [token.token_type for token in tokens2]
    assert types1 == types2
