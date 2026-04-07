import os
from jinja2 import Environment, FileSystemLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

env = Environment(loader=FileSystemLoader(BASE_DIR))
template = env.get_template('test.html')
# env = Environment(loader=FileSystemLoader('.'))

# template = env.get_template('E:/Intern Work/Python/python/13 PDF Report Generator with Templating/learning/test.html')
print("hello")
output = template.render(name='CrewAI')


with open('output.html', 'w') as f:

    f.write(output)
