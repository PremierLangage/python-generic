from json import load
from os import listdir


def build_pl_file(exercise_path,
                  template_file='../../templates/generic/generic.pl'):
    with open(exercise_path + ".pl", "w") as plfile:
        plfile.write(f"extends = {template_file}\n")
        if 'metadata.json' in listdir(exercise_path):
            with open(exercise_dir + '/metadata.json') as metadata:
                metadata = load(metadata)
                for key, val in sorted(metadata.items()):
                    plfile.write(f"{key} = {val}\n")
        plfile.write("\ntext ==\n")
        with open(exercise_path + "/enonce.md") as enonce:
            plfile.write(enonce.read())
        plfile.write("==\n")
        plfile.write("\ngrader ==\n")
        with open(exercise_path + "/grader.py") as grader:
            plfile.write(grader.read())
        plfile.write("==\n")


if __name__ == "__main__":
    with open("exercises/targets.txt") as fd:
        exlist = fd.read().strip().split('\n')
    for exercise_dir in exlist:
        if not exercise_dir.startswith('#'):
            build_pl_file(exercise_dir)
