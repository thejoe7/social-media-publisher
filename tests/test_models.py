from social_media_publisher.models import AuthConfig, PostContent, SocialPost

def test_models():
    auth = AuthConfig(cookie_file="cookies.json")
    content = PostContent(title="Test Title", body="Test Body", hashtags=["#test"], image_paths=["img.jpg"])
    post = SocialPost(platform="rednote", auth=auth, content=content)
    
    assert post.platform == "rednote"
    assert post.auth.cookie_file == "cookies.json"
    assert post.content.title == "Test Title"
    assert "#test" in post.content.hashtags
    print("test_models passed")

if __name__ == "__main__":
    test_models()
