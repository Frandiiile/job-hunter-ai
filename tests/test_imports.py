"""
Test that all imports work correctly.
This catches broken imports early.
"""


def test_scoring_imports():
    """Test scoring module imports."""
    from src.job_hunter_ai.scoring import (
        compute_deterministic_score,
        compute_hybrid_score,
    )
    assert callable(compute_deterministic_score)
    assert callable(compute_hybrid_score)


def test_llm_imports():
    """Test LLM module imports."""
    from src.job_hunter_ai.llm.enrich import (
        generate_master_cv,
        generate_cover_letter,
        compress_to_one_page,
        enrich_with_llm,
    )
    assert callable(generate_master_cv)
    assert callable(enrich_with_llm)


def test_latex_imports():
    """Test LaTeX module imports."""
    from src.job_hunter_ai.latex.render_template import (
        render_cv_template,
        render_cover_template,
        render_template,
        latex_escape,
    )
    assert callable(render_cv_template)
    assert callable(render_template)
    assert callable(latex_escape)


def test_drive_imports():
    """Test Drive module imports."""
    from src.job_hunter_ai.drive.upload import upload_to_drive
    assert callable(upload_to_drive)


def test_config_imports():
    """Test config module imports."""
    from src.job_hunter_ai.config import (
        GROQ_MODEL,
        get_profile_path,
        get_prompt_path,
    )
    assert isinstance(GROQ_MODEL, str)
    assert callable(get_profile_path)


def test_package_level_imports():
    """Test package-level imports work."""
    from src.job_hunter_ai import (
        compute_hybrid_score,
        compute_deterministic_score,
    )
    assert callable(compute_hybrid_score)
    assert callable(compute_deterministic_score)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
