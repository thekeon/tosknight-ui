"""Generate Documentation"""

import logging
import os
import tempfile
from subprocess import call
import datetime
import markdown
import yaml
import jinja2
import click

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

meta_file = '.meta.yml'
HTMLURL = 'https://siglt.github.io/tosknight-storage/'
MARKDOWNURL = 'https://github.com/siglt/tosknight-storage/blob/master/'

class Generator(object):
    def __init__(self, root, env):
        self.source_generator = SourceGenerator(root, env)
        self.cover_generator = CoverGenerator(env)

    def generate(self):
        self.cover_generator.generate()
        self.source_generator.generate()


class CoverGenerator(object):
    def __init__(self, env):
        self.ui_dir = output_dir
        self.env = env

    def generate(self):
        cover_template = self.env.get_template('index.jinja')
        with open(os.path.join(self.ui_dir, 'index.html'), 'w+') as f:
            f.write(cover_template.render())


class SourceGenerator(object):
    def __init__(self, root, env):
        self.root_dir = root
        self.env = env
        self.output_html_dir = output_source_dir
        self.categories = []
        self.source_items = []

    def generate(self):
        self.parse_category()
        self.render_source_index()

    def parse_category(self):
        for directory in os.listdir(self.root_dir):
            # If it is not README.md, parse it.
            sourcedir = os.path.join(self.root_dir, directory)
            if os.path.isdir(sourcedir) and os.path.basename(sourcedir) != '.git':
                mkdir_p(os.path.join(self.output_html_dir, os.path.basename(sourcedir)))
                category, caturl = self.parse_meta(os.path.join(sourcedir, meta_file))
                for filename in os.listdir(sourcedir):
                    if filename[0] == '.':
                        continue
                    elif '.html' in filename:
                        continue
                    item = SourceSnapshot(directory, os.path.join(directory, filename), category)
                    self.render_source_item(os.path.join(self.output_html_dir, os.path.basename(sourcedir)), item)
                    self.source_items.append(item)

    def parse_meta(self, file_name):
        with open(file_name) as f:
            raw_yaml_doc = f.read()
            yaml_obj = yaml.load(raw_yaml_doc)
            self.categories.append(yaml_obj['name'])
            return yaml_obj['name'], yaml_obj['url']

    def render_source_item(self, directory, item):
        source_template = self.env.get_template(
            'source_item_template.jinja')
        with open(os.path.join(directory, ('%s.index.html' % item.name)), 'w+') as f:
            f.write(source_template.render(
                item=item, today=datetime.datetime.now().ctime()))
        pass

    def render_source_index(self):
        categories = dict()
        for item in self.source_items:
            path = item.category
            if path not in categories:
                categories[path] = list()
            categories[path].append(item)
        elements = list()
        current_cat = None
        for cat in self.categories:
            if cat != current_cat:
                if current_cat is not None:
                    elements.append({'type': 'end-category', 'content': None})
                elements.append({'type': 'start-category', 'content': cat})
                current_cat = cat
            elements.append({'type': 'start-list', 'content': None})
            for item in sorted(categories[cat], key=lambda x: x.name):
                elements.append({'type': 'link', 'content': item})
            elements.append({'type': 'end-list', 'content': None})
        elements.append({'type': 'end-category', 'content': None})

        index_template = self.env.get_template(
            'source_index_template.jinja')
        with open(os.path.join(self.output_html_dir, 'index.html'), 'w+') as f:
            f.write(index_template.render(elements=elements))


class SourceSnapshot(object):
    def __init__(self, directory, absfilename, category):
        self.filename = absfilename
        # name is 2017-10-27-13:16:35.md
        self.name = os.path.basename(absfilename).split('.')[0]
        if self.name == 'latest':
            self.displayname = '最新文本'
        else:
            self.displayname = self.name + ' 备份文本'
        self.htmlname = ('%s.html' % self.name)
        self.markdownname = ('%s.md' % self.name)
        # category is the title of terms of service.
        self.category = category
        # directory is sha1(Source URL)
        self.directory = directory
        self.markdownURL = os.path.join(MARKDOWNURL, self.directory, self.markdownname)
        self.htmlURL = os.path.join(HTMLURL, self.directory, self.htmlname)
        self.path = os.path.join(directory, ('%s.index.html' % self.name))


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

@click.command()
@click.option('--storage-dir', default='', help='The location of tosknight storage')
@click.option('--ui-dir', default='', help='The location of tosknight UI')
def generate(storage_dir, ui_dir):
    '''Generate tosknight web UI.'''
    if ui_dir == '' or storage_dir == '':
        click.echo("The options are missed")
        exit

    click.echo('The location of tosknight storage: %s' % storage_dir)
    click.echo('The location of tosknight UI:      %s' % ui_dir)

    template_dir_short = 'templates'
    output_source_dir_short = 'docs/source'
    output_tutorial_dir_short = 'docs/tutorials'
    output_dir_short = 'docs'
    content_dir_short = 'content'
    tutorials_dir_short = 'tutorials'

    global template_dir
    global output_dir
    global content_dir
    global tutorials_dir
    global output_source_dir
    global output_tutorials_dir

    template_dir = os.path.join(ui_dir, template_dir_short)
    output_dir = os.path.join(ui_dir, output_dir_short)
    content_dir = os.path.join(ui_dir, content_dir_short)
    tutorials_dir = os.path.join(ui_dir, tutorials_dir_short)
    output_source_dir = os.path.join(ui_dir, output_source_dir_short)
    output_tutorials_dir = os.path.join(ui_dir, output_tutorial_dir_short)

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(
        template_dir), trim_blocks='true')

    generator = Generator(storage_dir, env)
    generator.generate()


if __name__ == '__main__':
    generate()
