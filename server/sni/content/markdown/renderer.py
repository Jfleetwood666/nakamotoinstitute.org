from typing import Dict, Optional, Sequence, Tuple

import yaml
from markdown_it import MarkdownIt
from markdown_it.renderer import RendererHTML, RendererProtocol
from markdown_it.token import Token
from markdown_it.utils import EnvType, OptionsDict
from mdit_py_plugins.deflist import deflist_plugin
from mdit_py_plugins.dollarmath import dollarmath_plugin
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.front_matter import front_matter_plugin


def render_math_inline(
    self: RendererProtocol,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
):
    return f"<span class='language-math math-inline'>{tokens[idx].content}</span>"


def render_math_block(
    self: RendererProtocol,
    tokens: Sequence[Token],
    idx: int,
    options: OptionsDict,
    env: EnvType,
) -> str:
    return f'<div class="language-math math-display">\n{tokens[idx].content}\n</div>\n'


class SNIMarkdownRenderer(RendererHTML):
    """
    Custom Markdown Renderer that can handle front matter.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._front_matter: Dict | None = None

    def front_matter(self, tokens, idx, options, env):
        self._front_matter = yaml.safe_load(tokens[idx].content)
        return self.renderToken(tokens, idx, options, env)


class MDRender:
    """
    Class to process Markdown files and convert them to HTML.
    Handles front matter using YAML.
    """

    @classmethod
    def process_md(cls, md_file_path: str) -> Tuple[Optional[Dict], str]:
        md = (
            MarkdownIt(
                "commonmark",
                {"breaks": False, "html": True},
                renderer_cls=SNIMarkdownRenderer,
            )
            .use(front_matter_plugin)
            .use(footnote_plugin)
            .use(deflist_plugin)
            .use(dollarmath_plugin)
        )

        md.add_render_rule("math_inline", render_math_inline)
        md.add_render_rule("math_block", render_math_block)

        file_content = cls._get_file_content(md_file_path)
        html_content = md.render(file_content).strip()

        return md.renderer._front_matter, html_content, file_content

    @classmethod
    def _get_file_content(cls, md_file_path: str) -> str:
        with open(md_file_path, "r", encoding="utf-8") as reader:
            return reader.read()
