def test_streamlit_app_preserves_synthetic_data_disclaimer(project_root):
    app_source = (
        project_root / "app" / "streamlit_app.py"
    ).read_text(encoding="utf-8").casefold()

    assert "synthetic dataset" in app_source
    assert "not financial advice" in app_source
