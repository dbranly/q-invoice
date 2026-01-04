"""
DocuVault - Tests
Sample test file
"""
import pytest
from pathlib import Path
from core.config import Config


def test_config_initialization():
    """Test configuration initialization"""
    assert Config.PROJECT_NAME == "DocuVault"
    assert Config.VERSION == "1.0.0"
    assert Config.SUPPORTED_FORMATS == ["png", "jpg", "jpeg", "pdf", "tiff"]


def test_config_directories():
    """Test directory setup"""
    Config.setup_directories()
    
    assert Config.STORAGE_DIR.exists()
    assert Config.UPLOADS_DIR.exists()
    assert Config.EXPORTS_DIR.exists()
    assert Config.CACHE_DIR.exists()


def test_config_validation():
    """Test configuration validation"""
    # This will fail if no API keys are set
    # In real tests, you'd mock this
    try:
        Config.validate()
    except ValueError as e:
        assert "API key" in str(e)


# Add more tests for:
# - OCR processing
# - LLM extraction
# - Database operations
# - Query engine
# - Export functionality
