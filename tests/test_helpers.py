"""
Test helper utilities for graceful error handling
"""
import functools
import traceback
import pytest


def handle_test_errors(func):
    """Decorator to handle test errors gracefully and continue testing"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as e:
            # Re-raise assertion errors as they are expected test failures
            raise
        except KeyError as e:
            # Handle missing fields gracefully
            pytest.fail(f"Missing expected field: {e}. API response format may have changed.")
        except Exception as e:
            # Log unexpected errors with full traceback
            traceback.print_exc()
            pytest.fail(f"Unexpected error in {func.__name__}: {type(e).__name__}: {e}")
    return wrapper


def assert_field_exists(obj, field, default=None):
    """Assert that a field exists in an object, handling both snake_case and kebab-case"""
    # Try both snake_case and kebab-case versions
    snake_case = field
    kebab_case = field.replace('_', '-')
    
    if snake_case in obj:
        return obj[snake_case]
    elif kebab_case in obj:
        return obj[kebab_case]
    elif default is not None:
        return default
    else:
        raise KeyError(f"Field '{field}' not found in object (tried '{snake_case}' and '{kebab_case}')")


def safe_get(obj, field, default=None):
    """Safely get a field from an object, handling both snake_case and kebab-case"""
    snake_case = field
    kebab_case = field.replace('_', '-')
    
    return obj.get(snake_case, obj.get(kebab_case, default))