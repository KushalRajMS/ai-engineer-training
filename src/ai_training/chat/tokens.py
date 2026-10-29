class ITokenServices:
    def estimate_tokens(self, text: str) -> int:
        words_count = len(text.split())
        return int(words_count * 1.3)


if __name__ == "__main__":
    estimate_token = ITokenServices()

    print(estimate_token.estimate_tokens(""))
    print(estimate_token.estimate_tokens(" "))
    print(estimate_token.estimate_tokens(" Hello, I am a helpful assistant. I can resolve and analyse all the question you ask on trading daily. Feel free to  ask me      anything. :)"))