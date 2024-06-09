from PIL import Image, ImageFont, ImageDraw


class ImageHelper:
    def __init__(self, template_path: str, result_path: str) -> None:
        self.template = Image.open(template_path)
        self.result_path = result_path

        self.drawer = ImageDraw.Draw(self.template)
        self.font = ImageFont.truetype("arial.ttf", 50)

        self.ABSENT = (58, 58, 60)
        self.PRESENT = (181, 159, 59)
        self.CORRECT = (83, 141, 78)

        self.START_COORD = 12
        self.SQUARE_WIDTH = 60
        self.SQUARE_OFFSET = 67

    def calculate_colors(self, word: str, target: str) -> list[tuple[int]]:
        target_letter_count = {l: target.count(l) for l in target}
        colors = [None] * len(word)

        # find grey and green letters
        for i in range(len(word)):
            if word[i] not in target:
                colors[i] = self.ABSENT
            elif word[i] == target[i]:
                colors[i] = self.CORRECT

        # find yellow letters
        for i in range(len(word)):
            if colors[i] is None:
                x = target_letter_count[word[i]]
                z = sum(word[i] == word[j] == target[j] for j in range(len(word)))

                cnt = 0
                for j in range(len(word)):
                    if word[i] == word[j] and colors[j] is None:
                        colors[j] = (
                            self.PRESENT
                            if cnt < (x if z == 0 else x - z)
                            else self.ABSENT
                        )
                        cnt += 1

        return colors

    def draw(self, words: list[str], target: str) -> None:
        target = target.upper()

        for i in range(len(words)):
            y1, y2 = (
                self.START_COORD + i * self.SQUARE_OFFSET,
                self.START_COORD + self.SQUARE_WIDTH + i * self.SQUARE_OFFSET,
            )

            word = words[i].upper()
            colors = self.calculate_colors(word, target)
            for j in range(len(word)):
                x1, x2 = (
                    self.START_COORD + j * self.SQUARE_OFFSET,
                    self.START_COORD + self.SQUARE_WIDTH + j * self.SQUARE_OFFSET,
                )

                self.drawer.rectangle([(x1, y1), (x2, y2)], fill=colors[j])

                w, h = self.font.getsize(word[j])
                text_x = x1 + 32 - w / 2
                text_y = y1 + 26 - h / 2
                self.drawer.text(
                    (text_x, text_y),
                    word[j],
                    (255, 255, 255),
                    font=self.font,
                    stroke_width=2,
                )

        self.template.save(self.result_path)
