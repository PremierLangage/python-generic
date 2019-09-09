class Feedback:
    def __init__(self, title=None, grade=0, template=None, items=None,
                 text=""):
        self.title = title
        self.grade = grade
        self.template = template
        self.items = [] if items is None else items
        self.text = text

    def set_mean_grade(self):
        if not self.items:
            raise ValueError("no items in mean grade computation")
        self.grade = sum(item.grade for item in self.items) // len(self.items)

    def subtest(self, item):
        self.items.append(item)

    def __str__(self):
        sp = do_spaces(self.template)
        res = sp + "[{}] {} (note: {})".format(
            self.template, self.title, self.grade)
        if self.items:
            res += "\n" + "\n".join(map(str, self.items))
        if self.text:
            res += "\n" + sp + "  " + self.text
        return res


def do_spaces(template):
    if template == "group":
        return " " * 2
    elif template == "unit":
        return " " * 4
    elif template == "detail":
        return " " * 6
    else:
        return " " * 0