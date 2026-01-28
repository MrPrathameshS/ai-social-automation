from app.db.models import GeneratedContent


def post_to_linkedin_mock(content: GeneratedContent):
    """
    Mock LinkedIn poster – just prints to console
    """
    print("\n================= 🚀 LINKEDIN POST =================")
    print(content.content_text)
    print("====================================================\n")
