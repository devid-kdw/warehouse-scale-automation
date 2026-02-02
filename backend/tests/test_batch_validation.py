"""Tests for batch validation."""
import pytest

from app.services.validation import validate_batch_code
from app.error_handling import AppError


class TestBatchCodeValidation:
    """Test batch code validation rules.
    
    Valid formats:
    - 4-5 digits (Mankiewicz): 0044, 1045, 10455
    - 9-12 digits (Akzo): 292456953, 2924662112, 292466211255
    """
    
    def test_valid_4_digits(self, app):
        """4 digit codes are valid."""
        with app.app_context():
            assert validate_batch_code('0044') is True
            assert validate_batch_code('1234') is True
            assert validate_batch_code('9999') is True
    
    def test_valid_5_digits(self, app):
        """5 digit codes are valid."""
        with app.app_context():
            assert validate_batch_code('10455') is True
            assert validate_batch_code('00001') is True
            assert validate_batch_code('99999') is True
    
    def test_valid_9_digits(self, app):
        """9 digit codes are valid."""
        with app.app_context():
            assert validate_batch_code('292456953') is True
            assert validate_batch_code('123456789') is True
    
    def test_valid_10_digits(self, app):
        """10 digit codes are valid."""
        with app.app_context():
            assert validate_batch_code('2924662112') is True
            assert validate_batch_code('0000000001') is True
    
    def test_valid_11_digits(self, app):
        """11 digit codes are valid."""
        with app.app_context():
            assert validate_batch_code('29246621125') is True
    
    def test_valid_12_digits(self, app):
        """12 digit codes are valid."""
        with app.app_context():
            assert validate_batch_code('292466211255') is True
    
    def test_invalid_3_digits(self, app):
        """3 digit codes are invalid (too short)."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('123')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_6_digits(self, app):
        """6 digit codes are invalid (in the gap)."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('123456')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_7_digits(self, app):
        """7 digit codes are invalid (in the gap)."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('1234567')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_8_digits(self, app):
        """8 digit codes are invalid (in the gap)."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('12345678')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_13_digits(self, app):
        """13 digit codes are invalid (too long)."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('1234567890123')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_non_numeric(self, app):
        """Non-numeric codes are invalid."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('abc123')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_with_hyphen(self, app):
        """Codes with hyphens are invalid."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('12-34')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
    
    def test_invalid_empty(self, app):
        """Empty codes are invalid."""
        with app.app_context():
            with pytest.raises(AppError) as exc:
                validate_batch_code('')
            assert exc.value.code == 'INVALID_BATCH_FORMAT'
