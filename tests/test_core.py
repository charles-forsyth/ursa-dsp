from ursa_dsp.core.rag import KnowledgeBase
from ursa_dsp.core.generator import DSPGenerator
from ursa_dsp.utils.io import read_file_content


def test_read_file_content(tmp_path):
    d = tmp_path / "test.txt"
    d.write_text("hello", encoding="utf-8")
    assert read_file_content(str(d)) == "hello"


def test_knowledge_base_loading(tmp_path):
    # Setup dummy example
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "test_example.txt").write_text(
        "This is a test example.\nTitle: Test Section\nBody content.", encoding="utf-8"
    )

    kb = KnowledgeBase(examples_dir=str(examples_dir))
    assert len(kb.examples) == 1
    assert "Test Section" in kb.examples[0]


def test_rag_full_context(tmp_path):
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    content = "Start\nSection 1\nRelevant content here.\n\nSection 2\nOther content."
    (examples_dir / "ex1.txt").write_text(content, encoding="utf-8")

    kb = KnowledgeBase(examples_dir=str(examples_dir))
    full_context = kb.get_full_context()
    assert "Relevant content here" in full_context
    assert "--- START EXAMPLE DSP:" in full_context


def test_generator_mock(mock_genai):
    gen = DSPGenerator()
    # Updated signature: section_title, section_body, project_summary, full_context
    _, content = gen.generate_section("Title", "Body", "Summary", "Full Context")
    assert content == "Mocked Content"
