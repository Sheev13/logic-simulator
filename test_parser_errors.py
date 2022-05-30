import pytest

"""
useful prompts for running pytest

pytest -q test_parser_errors.py --> run in 'quiet' mode

pytest test_parser_errors.py::TestParserDevicesErrors::test_parse_device_id 
--> run a specific tes

"""

class TestParserDevicesErrors:

    def test_parse_device_list(self):
        # can check if the total number of errors is correct?
        a = 1
        b = 2
        assert a+b == 3
        #could test which devices are created successfully? maybe


    def test_parse_device(self):
        # can check if:
        # after parsing open curly, parse_device_id is called,
        # then parse_device_kind, then parse_device_qual
        # and only if parse device qual is given
        #

        # if qual = bebop, error is not in qual but in lack of closing curly
        # bracket

        # OOOOH
        # i think need to test the semantic error throwing bc that is the
        # main stuff being done outside of the other functions

        # eg test error type that is returned

        # test that we do not build the device if there is > 0 syntax errors

        # test that the error recovery and the

        # missing semi colon at the end stuff....
        pass

    def test_parse_device_id(self):
        # if something goes wrong in the "id:name;" block (eg id or : or name)
        # isn't there,  test that error
        # recovery means we can go on to
        # parse the device kind if it is given there correctly

        #test that the SYNTACTIC checking of the name is happening
        # this is an assert that the returned device name is none?
        # i guess that will work

        # test missing semicolon
        pass


    def test_parse_device_kind(self):
        # similar to the above

        # could test semantics

        # also those times when we can expect TWO possible error recovery
        # stopping codes

        # bc the error recovery is pretty compartementalised
        pass

    def test_parse_device_qual(self):
        # test if the optionality of the function pulls thru

        # similar to the aforementioned functions
        pass


class TestParserConnectionsErrors:

    def test_connections_list(self):
        a=4
        b=8
        assert b-a == 4