import pytest
# import pytest-mock need to install this...?

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


def get_symbol_generator():
    dummy_parser = new_parser("test_files/blank.txt")
    return dummy_parser


dummy_parser = get_symbol_generator()


class TestParserDevices:

    @pytest.mark.parametrize("symbol_list, success, expected_error_count, "
                             "parse_device_call_number",
                             [
                                 ([dummy_parser.scanner.OPEN_SQUARE,
                                   dummy_parser.scanner.OPEN_CURLY,
                                   dummy_parser.scanner.SEMICOLON,
                                   dummy_parser.scanner.CONNECTIONS_ID],
                                  True,
                                  0, 1),  # device_list_is_perfect
                                 ([dummy_parser.scanner.OPEN_SQUARE,
                                   dummy_parser.scanner.OPEN_CURLY,
                                   dummy_parser.scanner.DEVICES_ID,
                                   dummy_parser.scanner.CONNECTIONS_ID],
                                  False,
                                  1, 1),  # one error will be reported (no semi
                                 # colon at end of device list)
                                 ([dummy_parser.scanner.CLOSE_SQUARE,
                                   dummy_parser.scanner.OPEN_CURLY,
                                   dummy_parser.scanner.DEVICES_ID,
                                   dummy_parser.scanner.CONNECTIONS_ID],
                                  False,
                                  1, 0),  # as soon as one error is reported we
                                 # break and skip to connections (no calls
                                 # to parse devices are made)

                             ])
    def test_parse_device_list(self, mocker, symbol_list, success,
                               expected_error_count, parse_device_call_number):
        """Completely patched test for Parser.parse_device_list which tests
        for correct handling for errors in the outer 'wrapping' for a
        DEVICES list (assumes that Parser.parse_device reaches the end of
        all the devices and that Parser.setNext always returns the correct
        symbol)"""

        parser_obj = new_parser("test_files/blank.txt")
        parser_obj.symbol = Symbol()

        def symbol_generator(sym_list):
            return (x for x in sym_list)

        gen = symbol_generator(symbol_list)

        # ^ this could become a pytest fixture

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        # Parser.error is patched so that we do not test scanner.show_error
        mocker.patch('parse.Parser.error', mock_error)

        def mock_set_next(self):
            parser_obj.symbol.id = next(gen)
            return

        # Parser.setNext is patched so that we do not test scanner functionality
        mocker.patch('parse.Parser.setNext', mock_set_next)

        def mock_parse_device(self, err):
            parser_obj.symbol.id = parser_obj.scanner.CLOSE_SQUARE
            return False

        # Parser.parse_device is patched so that we are only testing the
        # actual parse_device_list function
        mocker.patch('parse.Parser.parse_device', mock_parse_device)

        spy = mocker.spy(parser_obj, "parse_device")

        assert parser_obj.parse_devices_list() == success
        assert parser_obj.error_count == expected_error_count
        assert spy.call_count == parse_device_call_number

    def test_parse_device_semantic(self, mocker):
        """test if a semantic error will be detected and handled correctly"""

        parser_obj = new_parser("test_files/parse_device_semantic_error.txt")
        parser_obj.setNext()

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)

        spy_semantic = mocker.spy(parser_obj, "semantic_error")
        spy_syntactic = mocker.spy(parser_obj, "error")
        assert not parser_obj.parse_device(0)  # no missing semicolon
        assert spy_semantic.call_count == 1  # semantic error is detected
        assert spy_syntactic.call_count == 0  # no syntax error detected

    def test_parse_device_missing_semicolon_handling(self, mocker):
        """ if one of parse_device_id/parse_device_kind/parse_device_qual
        return a missing semicolon, we will skip to the next device"""

        # test eg if parse_device_id returns misisng semicolon, no calls to
        # device kind or device qual are made

        parser_obj = new_parser(
            "test_files/parse_device_missing_semicolon_handling.txt")
        parser_obj.setNext()

        mocker.patch('parse.Parser.parse_device_id', return_value=(True, None))

        spy_id = mocker.spy(parser_obj, "parse_device_id")
        spy_kind = mocker.spy(parser_obj, "parse_device_kind")
        spy_qual = mocker.spy(parser_obj, "parse_device_qual")

        parser_obj.parse_device(0)
        assert spy_id.call_count == 1  # called but missing semicolon
        assert spy_kind.call_count == 0  # not called
        assert spy_qual.call_count == 0  # not called

    @pytest.mark.parametrize("text_file, syntax_errors, semantic_errors",
                             [
                                 ("parse_device_optional_qual.txt", 0, 0),
                                 ("parse_device_should_have_qual.txt", 0, 1)
                             ])
    def test_parse_device_optional_qual(self, mocker, text_file,
                                        semantic_errors, syntax_errors):
        """Test that if qualifier is not given, the parsing of the device can
        continue regardless if qualifier is semantically necessary"""
        parser_obj = new_parser(f"test_files/{text_file}")
        parser_obj.setNext()

        spy_qual = mocker.spy(parser_obj, "parse_device_qual")
        spy_syntactic = mocker.spy(parser_obj, "error")
        spy_semantic = mocker.spy(parser_obj, "semantic_error")

        parser_obj.parse_device(0)
        assert spy_qual.call_count == 0  # correctly skipped
        assert spy_semantic.call_count == semantic_errors
        assert spy_syntactic.call_count == syntax_errors

    @pytest.mark.parametrize("text_file, missing_semicolon, device_name, "
                             "error_calls",
                             [
                                 ("device_id_correct.txt", False, "A", 0),
                                 # ("device_id_name_syntax.txt",False,None,1),
                                 ("device_id_missing.txt", False, None, 1),
                                 ("device_id_missing_semicolon.txt", True,
                                  "A", 1),
                             ])
    def test_parse_device_id(self, mocker, text_file, missing_semicolon,
                             device_name, error_calls):
        """Test that if something is wrong with a 'id:name;' block in
        definition file, the appropriate error will be thrown"""

        parser_obj = new_parser(f"test_files/{text_file}")
        parser_obj.setNext()

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)

        spy_parse_device_id = mocker.spy(parser_obj, "parse_device_id")
        spy_error = mocker.spy(parser_obj, "error")

        parser_obj.parse_device_id()
        assert spy_parse_device_id.spy_return == (
        missing_semicolon, device_name)
        assert spy_error.call_count == error_calls

    @pytest.mark.parametrize("text_file, missing_semicolon, "
                             "device_kind_string, "
                             "error_calls",
                             [
                                 ("device_kind_correct.txt", False, "NOR", 0),
                                 ("device_kind_simple_syntax.txt", False, None,
                                  1),
                                 ("device_kind_missing.txt", False, None, 1),
                                 ("device_kind_missing_semicolon.txt", True,
                                  "NOR", 1),
                             ])
    def test_parse_device_kind(self, mocker, text_file, missing_semicolon,
                               device_kind_string, error_calls):
        """Test that if something is wrong with a 'kind:kind;' block in
        definition file, the appropriate error will be thrown"""
        parser_obj = new_parser(f"test_files/{text_file}")
        parser_obj.setNext()

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)

        spy_parse_device_kind = mocker.spy(parser_obj, "parse_device_kind")
        spy_error = mocker.spy(parser_obj, "error")

        parser_obj.parse_device_kind()
        assert spy_parse_device_kind.spy_return[0] == missing_semicolon
        assert spy_parse_device_kind.spy_return[1] == device_kind_string
        assert spy_error.call_count == error_calls

    @pytest.mark.parametrize("text_file, missing_semicolon, "
                             "syntax_errors",
                             [
                                 ("device_qual_correct.txt", False, 0),
                                 ("device_qual_not_number.txt", False, 1),
                                 ("device_qual_missing.txt", False, 1),
                                 (
                                 "device_qual_missing_semicolon.txt", True, 1),
                             ])
    def test_parse_device_qual(self, mocker, text_file, missing_semicolon,
                               syntax_errors):
        parser_obj = new_parser(f"test_files/{text_file}")
        parser_obj.setNext()

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)

        spy_parse_device_qual = mocker.spy(parser_obj, "parse_device_qual")
        spy_error = mocker.spy(parser_obj, "error")

        parser_obj.parse_device_qual()
        assert spy_parse_device_qual.spy_return[0] == missing_semicolon
        assert spy_error.call_count == syntax_errors


class TestParserConnections:

    @pytest.mark.parametrize("symbol_list, success, setNext_count, "
                             "error_count",
                             [
                                 ([dummy_parser.scanner.OPEN_SQUARE,
                                   None,  # could be anything
                                   dummy_parser.scanner.SEMICOLON,
                                   None],  # could be anything
                                  True,
                                  4, 0),
                                 ([dummy_parser.scanner.OPEN_SQUARE,
                                   None,  # could be anything
                                   dummy_parser.scanner.INVALID_CHAR,
                                   None],  # could be anything
                                  False,
                                  4, 1),
                                 ([dummy_parser.scanner.CLOSE_CURLY,
                                   None,  # could be anything
                                   dummy_parser.scanner.INVALID_CHAR,
                                   None],  # could be anything
                                  False,
                                  2, 1),
                             ])
    def test_parse_connections_list_wrapper(self, mocker, symbol_list, success,
                                            setNext_count, error_count):
        parser_obj = new_parser(f"test_files/blank.txt")
        parser_obj.symbol = Symbol()

        def symbol_generator(sym_list):
            return (x for x in sym_list)

        gen = symbol_generator(symbol_list)

        def mock_set_next(self):
            parser_obj.symbol.id = next(gen)
            return

        # Parser.setNext is patched so that we do not test scanner functionality
        mocker.patch('parse.Parser.setNext', mock_set_next)

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)

        def mock_parse_connection(self, err):
            # parser_obj.symbol.id = parser_obj.scanner.DEVICES_ID
            # TODO: need to sort problem in parse.py
            parser_obj.symbol.id = parser_obj.scanner.CLOSE_SQUARE
            return False

        mocker.patch('parse.Parser.parse_connection', mock_parse_connection)

        spy_setNext = mocker.spy(parser_obj, "setNext")
        spy_error = mocker.spy(parser_obj, "error")

        assert parser_obj.parse_connections_list(0) == success
        assert spy_setNext.call_count == setNext_count
        assert spy_error.call_count == error_count

    def test_parse_connection_semantic(self, mocker):
        parser_obj = new_parser(
            "test_files/parse_connection_semantic_error.txt")
        parser_obj.setNext()

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)

        spy_semantic = mocker.spy(parser_obj, "semantic_error")
        spy_syntactic = mocker.spy(parser_obj, "error")
        assert not parser_obj.parse_connection(0)  # no missing semicolon
        assert spy_semantic.call_count == 1  # absent device syntax errors
        assert spy_syntactic.call_count == 0  # no syntax error detected

    @pytest.mark.parametrize("text_file, end_marker_missing, signal_name, "
                             "port_name, errors",
                             [
                                 ("A_signal.txt", False, "A", None, 0),
                                 ("G1I1_signal.txt", False,"G1", "I1", 0),
                                 ("missing_end_marker_signal.txt", True, "G1", "I1", 1),
                                 ("missing_port_name_signal.txt", False, "G1",
                                  "I1", 1),
                             ])
    def test_parse_signal(self, mocker, text_file, end_marker_missing,
                          signal_name,port_name,errors):
        parser_obj = new_parser(f"test_files/{text_file}")
        parser_obj.setNext()

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")

        mocker.patch('parse.Parser.error', mock_error)
        spy_syntactic = mocker.spy(parser_obj, "error")
        result = parser_obj.parse_signal()

        assert result[0] == end_marker_missing
        assert result[1] == parser_obj.names.query(signal_name)
        assert result[2] == parser_obj.names.query(port_name)
        assert spy_syntactic.call_count == errors


class TestParserMonitors:
    @pytest.mark.parametrize("symbol_list, success, setNext_count, "
                             "error_count",
                             [
                                 ([dummy_parser.scanner.OPEN_SQUARE,
                                   None,  # could be anything
                                   dummy_parser.scanner.SEMICOLON,
                                   None],  # could be anything
                                  True,
                                  4, 0),
                                 ([dummy_parser.scanner.OPEN_SQUARE,
                                   None,  # could be anything
                                   dummy_parser.scanner.INVALID_CHAR,
                                   None],  # could be anything
                                  False,
                                  4, 1),
                                 ([dummy_parser.scanner.CLOSE_CURLY,
                                   None,  # could be anything
                                   dummy_parser.scanner.INVALID_CHAR,
                                   None],  # could be anything
                                  False,
                                  2, 1),
                             ])
    def test_parse_monitors_list(self, mocker, symbol_list, success,
                                 setNext_count, error_count):
        parser_obj = new_parser(f"test_files/blank.txt")
        parser_obj.symbol = Symbol()

        def symbol_generator(sym_list):
            return (x for x in sym_list)

        gen = symbol_generator(symbol_list)

        def mock_set_next(self):
            parser_obj.symbol.id = next(gen)
            return
        # Parser.setNext is patched so that we do not test scanner functionality
        mocker.patch('parse.Parser.setNext', mock_set_next)

        def mock_error(self, msg, expt_list):
            parser_obj.error_count += 1
            print(f"SYNTAX ERROR FOUND: {msg}, recevied"
                  f" {parser_obj.strSymbol()}")
        mocker.patch('parse.Parser.error', mock_error)

        def mock_parse_monitor(self, err):
            parser_obj.symbol.id = parser_obj.scanner.CLOSE_SQUARE
            return False

        mocker.patch('parse.Parser.parse_monitor', mock_parse_monitor)

        spy_setNext = mocker.spy(parser_obj, "setNext")
        spy_error = mocker.spy(parser_obj, "error")

        assert parser_obj.parse_monitors_list(0) == success
        assert spy_setNext.call_count == setNext_count
        assert spy_error.call_count == error_count

    @pytest.mark.parametrize("text_file, syntax_errors, semantic_errors",
                             [
                                 ("parse_monitor_semantic.txt",  0, 1),
                                 ("parse_monitor_syntax_semantic.txt", 1, 1),
                             ])
    def test_parse_monitor_semantic(self, mocker, text_file, semantic_errors,
                            syntax_errors):
        parser_obj = new_parser(f"test_files/{text_file}")
        parser_obj.symbol = Symbol()

        spy_syntactic = mocker.spy(parser_obj, "error")
        spy_semantic = mocker.spy(parser_obj, "semantic_error")

        parser_obj.parse_network()
        assert spy_semantic.call_count == semantic_errors
        assert spy_syntactic.call_count == syntax_errors


class TestParserErrorRecovery:

    # can i test this without having to create all the other objects?
    # debatable

    def test_error_recovery_midfile(self):
        # may require mocking for self.scanner.show_error?
        pass

    def test_error_recovery_eof(self):
        # test wat happens if we reach the end of the file during error
        # recovery

        # is this doable???
        pass
