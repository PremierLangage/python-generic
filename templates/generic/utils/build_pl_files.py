from json import load
from os import listdir
from sys import argv


def pl_content(exercise_path, template_file):
    lines = [f"extends = {template_file}"]
    if 'metadata.json' in listdir(exercise_path):
        with open(exercise_dir + '/metadata.json') as fd:
            metadata = load(fd)
            for key, val in sorted(metadata.items()):
                lines.append(f"{key} = {val}")
    lines.append(f"text =@ {exercise_path}/enonce.md")
    lines.append(f"grader =@ {exercise_path}/grader.py")
    return "\n".join(lines)


def build_pl_file(exercise_path,
                  template_file='../templates/generic/generic.pl'):
    with open(exercise_path + ".pl", "w") as plfile:
        plfile.write(pl_content(exercise_path, template_file))


if __name__ == "__main__":
    with open("exercises/targets.txt") as fd:
        exlist = fd.read().strip().split('\n')
    for exercise_dir in exlist:
        build_pl_file(exercise_dir)
