# Based on https://github.com/vilcans/screenplain/blob/master/screenplain/export/pdf.py
# Original Work by Martin Vilcans
# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license.php

import sys
import os

try:
    import reportlab
except ImportError:
    sys.stderr.write('ERROR: ReportLab is required for PDF output\n')
    raise
del reportlab

from reportlab.lib import pagesizes
from reportlab.platypus import (
    BaseDocTemplate,
    Paragraph,
    Frame,
    PageTemplate,
    Spacer,
)
from reportlab import platypus
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import (registerFont, registerFontFamily)

def get_font(font=''):
    FONTS_PATH=os.path.dirname(os.path.abspath(__file__)) + '/'
    return FONTS_PATH + 'fonts/' + font

registerFont(TTFont('source-han-serif', get_font('SourceHanSerif-Light.ttc')))
registerFont(TTFont('source-han-serif-bold', get_font('SourceHanSans-Medium.ttc')))
registerFont(TTFont('source-han-sans', get_font('SourceHanSans-Regular.ttc')))
registerFont(TTFont('source-han-sans-bold', get_font('SourceHanSans-Medium.ttc')))
registerFontFamily('source-han-sans',normal='source-han-sans',bold='source-han-sans-bold',italic='source-han-sans',boldItalic='source-han-sans-bold')
registerFontFamily('source-han-serif',normal='source-han-serif',bold='source-han-serif-bold',italic='source-han-serif',boldItalic='source-han-serif-bold')

from screenplain.types import (
    Action, Dialog, DualDialog, Transition, Slug
)
from screenplain import types

font_size = 12
line_height = 18
lines_per_page = 38
characters_per_line = 33
character_width = 1.0 / 6 * inch  # source-han-serif pitch is 6 chars/inch
dialog_per_line = 21
dialog_left_indent = 5
frame_height = line_height * lines_per_page
frame_width = characters_per_line * character_width
scene_number = 1

page_width, page_height = pagesizes.letter
left_margin = 1.5 * inch
right_margin = page_width - left_margin - frame_width
top_margin = 1 * inch
bottom_margin = page_height - top_margin - frame_height

def beginTextWithSapce(self, x, y):
    tx = self.canv.beginText(x, y)
    try:
        if self.style.charSpace:
            tx.setCharSpace(self.style.charSpace)
    except:
        return tx
    return tx

Paragraph.beginText = beginTextWithSapce

default_style = ParagraphStyle(
    'default',
    fontName='source-han-serif',
    fontSize=font_size,
    leading=line_height,
    spaceBefore=0,
    spaceAfter=0,
    leftIndent=0,
    rightIndent=0,
    charSpace=1,
    underlineOffset=-3,
    underlineWidth=0.8,
    #wordWrap='CJK' # Not working perfectly
)
centered_style = ParagraphStyle(
    'default-centered', default_style,
    alignment=TA_CENTER,
)

# Screenplay styles
character_style = ParagraphStyle(
    'character', default_style,
    fontName='source-han-sans',
    spaceBefore=line_height,
    leftIndent=11.5 * character_width,
    keepWithNext=1,
)
dialog_style = ParagraphStyle(
    'dialog', default_style,
    leftIndent=dialog_left_indent * character_width,
    rightIndent=frame_width - (int(dialog_per_line + dialog_left_indent) * character_width),
)
parenthentical_style = ParagraphStyle(
    'parenthentical', default_style,
    leftIndent=9.8 * character_width,
    keepWithNext=1,
)
action_style = ParagraphStyle(
    'action', default_style,
    spaceBefore=line_height,
)

action_style_first_line_indent = ParagraphStyle(
    'action', default_style,
    spaceBefore=line_height,
    firstLineIndent=1.44,
)

centered_action_style = ParagraphStyle(
    'centered-action', action_style,
    alignment=TA_CENTER,
)
slug_style = ParagraphStyle(
    'slug', default_style,
    fontName='source-han-sans',
    spaceBefore=line_height*2,
    spaceAfter=line_height,
    keepWithNext=1,
    leftIndent=-40.8
)
transition_style = ParagraphStyle(
    'transition', default_style,
    spaceBefore=line_height,
    spaceAfter=line_height,
    alignment=TA_RIGHT,
)

# Title page styles
title_style = ParagraphStyle(
    'title', default_style,
    fontSize=16, leading=36,
    alignment=TA_CENTER,
)
contact_style = ParagraphStyle(
    'contact', default_style,
    leftIndent=2.9 * inch,
    rightIndent=0,
    fontName='source-han-serif',
    fontSize=12,
)

draft_style = ParagraphStyle(
    'draft', default_style,
    fontName='source-han-serif',
    fontSize=12,
    leftIndent=2.9 * inch,
    rightIndent=0,
)

class DocTemplate(BaseDocTemplate):
    def __init__(self, *args, **kwargs):
        self.has_title_page = kwargs.pop('has_title_page', False)
        self.first_page_number = kwargs.pop('first_page_number', False)
        frame = Frame(
            left_margin, bottom_margin, frame_width, frame_height,
            id='normal',
            leftPadding=0, topPadding=0, rightPadding=0, bottomPadding=0
        )
        pageTemplates = [
            PageTemplate(id='standard', frames=[frame])
        ]
        BaseDocTemplate.__init__(
            self, pageTemplates=pageTemplates, *args, **kwargs
        )

    def handle_pageBegin(self):
        self.canv.setFont('Courier', font_size, leading=line_height)
        if self.has_title_page:
            page = self.page  # self.page is 0 on first page
        else:
            page = self.page + 1
        num_start_page = 2
        if  self.first_page_number: num_start_page=1
        if page >= num_start_page:
            self.canv.drawRightString(
                left_margin + frame_width + 30 + len(str(self.page))*6,
                page_height - 42,
                '%s.' % page
            )
        self._handle_pageBegin()

def to_html(line):
    return line.to_html().replace(' ', '&nbsp;')

def add_paragraph(story, para, style):
    story.append(Paragraph(
        '<br/>'.join(to_html(line).replace(' ', '&nbsp;') for line in para.lines),
        style
    ))


def add_slug(story, para, style, is_strong, has_scene_num):
    global scene_number
    pad = 9 - len(str(scene_number)) 
    strong_left_tag = ''
    strong_right_tag = ''
    if is_strong:
        strong_left_tag = '<b>' 
        strong_right_tag = '</b>' 
    for line in para.lines:
        if has_scene_num:
            html = str(scene_number).rjust(pad,'_').replace('_', '&nbsp;') + strong_left_tag + '&nbsp;&nbsp;' + to_html(line) + strong_right_tag
        else:
            style.leftIndent = -7.8
            html = strong_left_tag + '&nbsp;&nbsp;' + to_html(line) + strong_right_tag
        scene_number += 1
        story.append(Paragraph(html, style))

def add_dialog(story, dialog):
    story.append(Paragraph(dialog.character.to_html(), character_style))
    for parenthetical, line in dialog.blocks:
        if parenthetical:
            story.append(Paragraph(to_html(line), parenthentical_style))
        else:
            story.append(Paragraph(to_html(line), dialog_style))


def add_dual_dialog(story, dual):
    # TODO: format dual dialog
    add_dialog(story, dual.left)
    add_dialog(story, dual.right)


def get_title_page_story(screenplay):
    """Get Platypus flowables for the title page

    """
    # From Fountain spec:
    # The recommendation is that Title, Credit, Author (or Authors, either
    # is a valid key syntax), and Source will be centered on the page in
    # formatted output. Contact and Draft date would be placed at the lower
    # left.

    def add_lines(story, attribute, style, space_before=0):
        lines = screenplay.get_rich_attribute(attribute)
        if not lines:
            return 0

        if space_before:
            story.append(Spacer(frame_width, space_before))

        total_height = 0
        for line in lines:
            html = to_html(line)
            para = Paragraph(html, style)
            width, height = para.wrap(frame_width, frame_height)
            story.append(para)
            total_height += height
        return space_before + total_height

    title_story = []
    title_height = sum((
        add_lines(title_story, 'Title', title_style),
        add_lines(
            title_story, 'Credit', centered_style, space_before=line_height
        ),
        add_lines(title_story, 'Author', centered_style),
        add_lines(title_story, 'Authors', centered_style),
        add_lines(title_story, 'Source', centered_style),
    ))

    lower_story = []
    lower_height = sum((
        add_lines(lower_story, 'Draft date', draft_style),
        add_lines(
            lower_story, 'Contact', contact_style, space_before=line_height
        ),
        add_lines(
            lower_story, 'Copyright', centered_style, space_before=line_height
        ),
    ))

    if not title_story and not lower_story:
        return []

    story = []
    top_space = min(
        frame_height / 3.0,
        frame_height - lower_height - title_height
    )
    if top_space > 0:
        story.append(Spacer(frame_width, top_space))
    story += title_story
    # The minus 6 adds some room for rounding errors and whatnot
    middle_space = frame_height - top_space - title_height - lower_height - 6
    if middle_space > 0:
        story.append(Spacer(frame_width, middle_space))
    story += lower_story

    story.append(platypus.PageBreak())
    return story


def to_pdf(
    screenplay, output_filename,
    template_constructor=DocTemplate,
    is_strong=False,
    has_scene_num=False,
    first_page_number=False,
    first_line_indent=False
):
    global scene_number
    scene_number = 1
    story = get_title_page_story(screenplay)
    has_title_page = bool(story)

    for para in screenplay:
        if isinstance(para, Dialog):
            add_dialog(story, para)
        elif isinstance(para, DualDialog):
            add_dual_dialog(story, para)
        elif isinstance(para, Action):
            add_paragraph(
                story, para,
                centered_action_style if para.centered else (action_style_first_line_indent if first_line_indent else action_style)
            )
        elif isinstance(para, Slug):
            add_slug(story, para, slug_style, is_strong, has_scene_num)
        elif isinstance(para, Transition):
            add_paragraph(story, para, transition_style)
        elif isinstance(para, types.PageBreak):
            story.append(platypus.PageBreak())
        else:
            # Ignore unknown types
            pass

    doc = template_constructor(
        output_filename,
        pagesize=(page_width, page_height),
        has_title_page=has_title_page,
        first_page_number=first_page_number
    )
    doc.build(story)
    slug_style.leftIndent=-40.8
