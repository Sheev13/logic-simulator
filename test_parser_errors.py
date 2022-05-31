import pytest
#import pytest-mock need to install this...?

from names import Names
from network import Network
from devices import Devices
from monitors import Monitors
from parse import Parser
from scanner import Scanner, Symbol

"""
useful prompts for running pytest

pytest -q test_parser_errors.py --> run in 'quiet' mode

pytest test_parser_errors.py::TestParserDevices::test_parse_device_id 
--> run a specific tes

"""


def new_parser(path):
    """Return a Parser class instance for given path."""
    new_names = Names()
    new_devices = Devices(new_names)
    new_network = Network(new_names, new_devices)
    new_monitors = Monitors(new_names, new_devices, new_network)
    new_scanner = Scanner(path, new_names)
    new_parser = Parser(
        new_names,
        new_devices,
        new_network,
        new_monitors,
        new_scanner
    )
    return new_parser



class TestParserDevices:

    def test_parse_device_list(self):
        # can check if the total number of errors is correct?

        #could test which devices are created successfully? maybe

        """
        [ {}; {}; {}; ];

        if self.parse_device returns false (no missing semicolons)
            if self.symbol.id = ]
            we assert that parse_device is no longer called
            we assert that self.error is not called if there is nothing wrong
            we assert that error_count == 0
            we assert that we returned True

        so need to mock self.setNext() (scanner)
        need to mock self.symbol.id (or maybe in setNext we can replace it
        with a function that sets self.symbol.id
        """
        parser_obj = new_parser("test_files/jessye_mess_about.txt")
        parser_obj.parse_devices_list()

    def test_parse_device_list_with_mocker(self, mocker):
        parser_obj = new_parser("test_files/jessye_mess_about.txt")
        # the path could literally be anything? bc we aren't using scanner
        # functionality
        parser_obj.symbol = Symbol()

        #this is the customisable code per test
        def generate_next_symbol():
            symbols = [
                parser_obj.scanner.OPEN_SQUARE,
                parser_obj.scanner.OPEN_CURLY,
                parser_obj.scanner.DEVICES_ID,
                parser_obj.scanner.CONNECTIONS_ID
            ]

            return (id for id in symbols)

        gen = generate_next_symbol()

        def mock_error(self,msg,error_call_count):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        def mock_set_next(self):
            print("before ", parser_obj.strSymbol())
            parser_obj.symbol.id = next(gen)
            print("after ", parser_obj.strSymbol())
            return

        def mock_parse_device(self, err):
            #par.setNext()
            #print(parser_obj.strSymbol())
            parser_obj.symbol.id = parser_obj.scanner.CLOSE_SQUARE
            return False
            #return False  # not missing semicolon


        mock_scanner_err_f = mocker.patch('parse.Parser.error', mock_error)

        mocker.patch('parse.Parser.setNext', mock_set_next)

        # can't get mocker spy to spy a patched function :/
        # spy = mocker.spy(
        #     parser_obj,
        #     "parse_device" )
        # spy.assert_called_once()

        mock_device = mocker.patch('parse.Parser.parse_device',
                                  mock_parse_device)

        assert not parser_obj.parse_devices_list()
        assert parser_obj.error_count == 1




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


class TestParserConnections:

    def test_parse_connections_list(self):
        pass

    def test_parse_connections(self):
        pass

    def test_parse_signal(self):
        pass


class TestParserMonitors:

    def test_parse_monitors_list(self):
        #missing semi colons
        pass

    def test_parse_monitor(self):
        #test the missing semicolon funciton?

        #the right number of errors
        pass


class TestParserErrorRecovery:

    # can i test this without having to create all the other objects?
    # debatable

    def test_error_recovery_midfile(self):
        # may require mocking for self.scanner.show_error?
        pass

    def test_error_recovery_eof(self):
        # test wat happens if we reach the end of the file during error
        # recovery

        #is this doable???
        pass