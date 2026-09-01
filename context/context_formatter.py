"""
ARUS Context Formatter
"""


class ContextFormatter:


    def format(
        self,
        history
    ):

        if not history:
            return ""


        result = []


        for item in history:

            role = item.get(
                "role",
                "user"
            )

            content = item.get(
                "content",
                ""
            )

            result.append(
                f"{role}: {content}"
            )


        return "\n".join(result)
