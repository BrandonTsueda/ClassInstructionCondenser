import unittest

from class_instruction_summarizer.summarizer import summarize_instructions


class SummarizerTests(unittest.TestCase):
    def test_empty_input_returns_guidance(self):
        result = summarize_instructions("")

        self.assertEqual("No instructions pasted yet", result.title)
        self.assertEqual([], result.requirements)

    def test_extracts_core_requirements(self):
        text = """
        Week 3 Discussion Assignment
        Due Sunday at 11:59 PM.
        Write an initial post of at least 300 words.
        Include two scholarly sources in APA format.
        Submit your response in the discussion board and reply to two classmates.
        This assignment is worth 50 points based on the rubric.
        """

        result = summarize_instructions(text)

        self.assertIn("Week 3 Discussion Assignment", result.title)
        self.assertTrue(any("300 words" in item for item in result.requirements))
        self.assertTrue(any("11:59" in item for item in result.dates))
        self.assertTrue(any("APA" in item for item in result.citations_formatting))
        self.assertTrue(any("50 points" in item for item in result.grading))

    def test_cleans_common_bullet_prefixes(self):
        text = """
        Assignment Requirements
        • Submit a 2 page reflection.
        - Include one source.
        1. Reply to two classmates.
        """

        result = summarize_instructions(text)
        combined = " ".join(result.requirements + result.submission + result.citations_formatting)

        self.assertIn("Submit a 2 page reflection", combined)
        self.assertIn("Include one source", combined)
        self.assertIn("Reply to two classmates", combined)


if __name__ == "__main__":
    unittest.main()
