import requests
from dataclasses import dataclass

@dataclass
class VerificationMessage:
    text: str
    msg_id: int

class VerificationError(Exception):
    pass

class XYZVerifier:
    def __init__(self, base_url: str = "https://xyz.ag3nts.org/verify"):
        self.url = base_url
        self.headers = {"Content-Type": "application/json"}

    def _post(self, payload: dict) -> VerificationMessage:
        response = requests.post(self.url, json=payload, headers=self.headers)

        if response.status_code != 200:
            raise VerificationError(
                f"HTTP {response.status_code}: {response.text}"
            )

        data = response.json()
        if "text" not in data or "msgID" not in data:
            raise VerificationError(
                f"Malformed response: {data}"
            )

        return VerificationMessage(text=data["text"], msg_id=data["msgID"])

    def start_verification(self) -> VerificationMessage:
        """Send the initial 'READY' message with msgID 0"""
        return self._post({"text": "READY", "msgID": 0})

    def answer_question(self, msg_id: int, answer: str) -> VerificationMessage:
        """Respond to robot's question using the given msgID"""
        return self._post({"text": answer, "msgID": msg_id})

# Example usage (optional for manual testing)
if __name__ == "__main__":
    verifier = XYZVerifier()
    try:
        initial = verifier.start_verification()
        print(f"🤖 Question: {initial.text} [msgID={initial.msg_id}]")

        user_input = input("Your answer: ")
        result = verifier.answer_question(initial.msg_id, user_input)
        print(f"✅ Result: {result.text}")
    except VerificationError as e:
        print(f"❌ Verification failed: {e}")