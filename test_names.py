"""Test the monitors module."""
import pytest

from names import Names


@pytest.fixture
def new_empty_names():
    """Return a Names class instance."""
    return Names()


@pytest.fixture
def new_names():
    """Return a Names class instance and initialises names."""
    names = Names()
    names.names_list = ['Sw1', 'Sw2']
    return names


def test_unique_error_codes(new_empty_names):
    """Test if unique_error_codes returns list of unique integer codes."""
    num_error_codes = 10
    codes = new_empty_names.unique_error_codes(num_error_codes)

    assert new_empty_names.error_code_count == num_error_codes
    assert codes == range(0, num_error_codes)


def test_unique_error_codes_gives_errors(new_empty_names):
    """Test if test_unique_error_codes raises correct errors."""
    num_error_codes = 4.44
    with pytest.raises(TypeError):
        new_empty_names.unique_error_codes(num_error_codes)


def test_query(new_names):
    """Test if query returns correct name ID for name_string."""
    assert new_names.query('Sw1') == 0
    assert new_names.query('Sw2') == 1
    assert new_names.query('yoohoo') is None


def test_lookup(new_names):
    """Test if lookup returns correct name IDs for present and new names."""
    # Test look up returns correct name ids for current names
    assert new_names.lookup(['Sw1', 'Sw2']) == [0, 1]

    # Test look up returns correct name ids for new names
    assert new_names.lookup(['Sw3', 'Sw4']) == [2, 3]

    # Test look up returns correct name ids for newly added names
    assert new_names.lookup(['Sw4', 'Sw1']) == [3, 0]

    # Test look up returns correct name ids for new and present names
    assert new_names.lookup(['Sw5', 'Sw3']) == [4, 2]


def test_lookup_gives_errors(new_names):
    """Test if lookup returns correct errors for invalid name_string."""
    invalid_name_string = ["yoohoo", 4.44]
    with pytest.raises(TypeError):
        new_names.lookup(invalid_name_string)


def test_get_name_string(new_names):
    """Test if get_name_string returns correct name."""
    assert new_names.get_name_string(0) == 'Sw1'
    assert new_names.get_name_string(1) == 'Sw2'


def test_get_name_string_gives_errors(new_names):
    """Test if get_name_string raises correct errors."""
    with pytest.raises(TypeError):
        new_names.get_name_string("yoohoo")
    with pytest.raises(ValueError):
        new_names.get_name_string(-1)
    with pytest.raises(ValueError):
        new_names.get_name_string(5)
