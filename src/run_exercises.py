
from grader import grade_this
from os import listdir, makedirs
from os.path import splitext
from sys import argv


def html_preamble(exercise_path, answer_filename):
    title = f"Feedback for exercise {exercise_path, answer_filename}"

    tmp = f'''
<!DOCTYPE HTML>
<html lang="fr">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
'''

    tmp += '''
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.5.0/css/all.css"
          integrity="sha384-B4dIYHKNBt8Bc12p+WXckhzcICo0wtJAoU8YZTY5qE0Id1GSseTk6S+L3BlXeVIU"
          crossorigin="anonymous">
    
    <!-- MathJax http://docs.mathjax.org/en/latest/start.html -->
    <script type="text/x-mathjax-config">
        MathJax.Hub.Config({
            tex2jax: {
                inlineMath: [['$%','%$'], ['$!', '!$']],
                skipTags: ["script", "noscript", "style"],
            }
        });
    </script>
    <script type="text/javascript" 
            src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"
            async></script>
    
    <!-- JQuery https://jquery.com/ -->
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"
            integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8="
            crossorigin="anonymous"></script>
    
    <!-- Bootstrap https://getbootstrap.com/ -->
    <link rel="stylesheet"
          href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
          integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
          crossorigin="anonymous">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js"
            integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
            crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js"
            integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
            crossorigin="anonymous"></script>
    
    <!-- Ionic -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@ionic/core@4.7.4/css/ionic.bundle.css"/>
    <script type="module" src="https://cdn.jsdelivr.net/npm/@ionic/core@4.7.4/dist/ionic/ionic.esm.js"></script>
    <script nomodule src="https://cdn.jsdelivr.net/npm/@ionic/core@4.7.4/dist/ionic/ionic.js"></script>
    <script type="module" src="https://cdn.jsdelivr.net/npm/ionicons@4.6.3/dist/ionicons/ionicons.esm.js"></script>
    <script nomodule="" src="https://cdn.jsdelivr.net/npm/ionicons@4.6.3/dist/ionicons/ionicons.js"></script>
    <script src="https://unpkg.com/@webcomponents/custom-elements"></script>
  </head>
  <body>
'''

    return tmp


def html_footer():
    return '''
  </body>
</html>
'''


def test_exercise(dirname):
    grader_file_name = dirname + '/grader.py'

    # gather answer file paths
    if 'answers' not in listdir(dirname):
        return
    answer_dirname = dirname + '/answers/'
    answer_basenames = listdir(answer_dirname)
    if not answer_basenames:
        return
    answer_paths = [answer_dirname + name
                    for name in answer_basenames]

    # create feedback dir and prepare feedback paths
    makedirs(dirname + '/feedback/', exist_ok=True)
    feedback_paths = [dirname + '/feedback/' + splitext(name)[0] + '.html'
                      for name in answer_basenames]

    # get exercise-specific grader file
    with open(grader_file_name) as grader_file:
        grader_code = grader_file.read()

    # grade each answer and write feedback
    for i in range(len(answer_paths)):
        with open(answer_paths[i]) as student_file:
            student_code = student_file.read()
        grade, fb = grade_this(student_code, grader_code, globals())
        with open(feedback_paths[i], 'w') as feedback_file:
            feedback_file.write(
                html_preamble(dirname, answer_basenames[i]))
            feedback_file.write(fb)
            feedback_file.write(html_footer())


if __name__ == "__main__":
    with open("exercises/targets.txt") as fd:
        exlist = fd.read().strip().split('\n')
    for exercise_dir in exlist:
        if not exercise_dir.startswith('#'):
            test_exercise(exercise_dir)
