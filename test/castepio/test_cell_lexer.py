from castepio import cell_lexer

def test_lex1():
    source1 = open("test/resources/c_dia_p010.cell").read()
    tokens1 = cell_lexer.Lexer.static_lex(source1)
    source2 = cell_lexer.Lexer.tokpass(source1)
    tokens2 = cell_lexer.Lexer.static_lex(source2)
    types1 = [token.token_type for token in tokens1]
    types2 = [token.token_type for token in tokens2]
    assert types1 == types2
