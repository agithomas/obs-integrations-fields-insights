from graph.chains.search_query_generator import dot_to_space

def test_dot_to_space():
    string = "oracle.tablespace.data_file.size.free.bytes"
    result = dot_to_space(string)
    assert(result == "oracle tablespace data_file size free bytes")

