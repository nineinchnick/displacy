import xml.etree.cElementTree as ETree
import spacy


class Displacy:
    def __init__(self, options=None):
        if options is None:
            options = {}
        self.word_distance = options.get('wordDistance', 200)
        self.arc_distance = options.get('arcDistance', 60)
        self.highest_level = 1
        self.offset_x = options.get('offsetX', 50)
        self.offset_y = self.arc_distance * self.highest_level
        self.arrow_spacing = options.get('arrowSpacing', 20)
        self.arrow_width = options.get('arrowWidth', 10)
        self.arrow_stroke = options.get('arrowStroke', 2)
        self.word_spacing = options.get('wordSpacing', 75)
        self.font = options.get('font', 'inherit')
        self.color = options.get('color', '#000000')
        self.bg = options.get('bg', '#ffffff')

    @staticmethod
    def words_and_arcs(doc, index_offset=0):
        words = [{'text': w.text, 'tag': w.tag_} for w in doc]
        arcs = []
        for word in doc:
            if word.i < word.head.i:
                arcs.append({'start': word.i - index_offset,
                             'end': word.head.i - index_offset,
                             'label': word.dep_,
                             'dir': 'left'})
            elif word.i > word.head.i:
                arcs.append({'start': word.head.i - index_offset,
                             'end': word.i - index_offset,
                             'label': word.dep_,
                             'dir': 'right'})
        return {'words': words, 'arcs': arcs}

    @staticmethod
    def collapse_doc(doc, collapse_punctuation=True, collapse_phrases=True):
        if collapse_punctuation:
            spans = []
            for word in doc[:-1]:
                if word.is_punct:
                    continue
                if not word.nbor(1).is_punct:
                    continue
                start = word.i
                end = word.i + 1
                while end < len(doc) and doc[end].is_punct:
                    end += 1
                span = doc[start: end]
                spans.append(
                    (span.start_char, span.end_char, word.tag_, word.lemma_, word.ent_type_)
                )
            for span_props in spans:
                doc.merge(*span_props)

        if collapse_phrases:
            for np in list(doc.noun_chunks):
                np.merge(np.root.tag_, np.root.lemma_, np.root.ent_type_)

    @staticmethod
    def check_levels(arcs):
        levels = []
        for arc in arcs:
            level = arc['end'] - arc['start']
            if level not in levels:
                levels.append(arc['end'] - arc['start'])
        levels = list(sorted(levels))

        for arc in arcs:
            arc['level'] = levels.index(arc['end'] - arc['start']) + 1
        return levels

    def render(self, parse, settings=None):
        if settings is None:
            settings = {}

        levels = self.check_levels(parse['arcs'])
        self.highest_level = len(levels) + 1
        self.offset_y = self.arc_distance * self.highest_level

        width = self.offset_x + len(parse['words']) * self.word_distance
        height = self.offset_y + 3 * self.word_spacing

        el = self._el('svg', {
            'id': 'displacy-svg',
            'classnames': ['displacy'],
            'attributes': [
                ['width', width],
                ['height', height],
                ['viewBox', '0 0 {} {}'.format(width, height)],
                ['preserveAspectRatio', 'xMinYMax meet'],
                ['data-format', 'spacy']
            ],
            'style': [
                ['color', settings.get('color', self.color)],
                ['background', settings.get('bg', self.bg)],
                ['fontFamily', settings.get('font', self.font)]
            ],
            'children': self.render_items(parse['words'], self.get_word_tag, settings.get('index_base', 0))
            + self.render_items(parse['arcs'], self.get_arrow_tag, settings.get('index_base', 0)),
        })
        return ETree.tostring(el, encoding='unicode')

    @staticmethod
    def get_data_attributes(data):
        result = []
        for item in data:
            result.append(['data-' + item['attr'].replace(' ', '-'), item['value']])
        return result

    @staticmethod
    def render_items(items, tag_method, tag_index_base):
        result = []
        index = 0
        for item in items:
            item['index'] = index
            item['tag_index'] = tag_index_base
            result.append(tag_method(item))
            index += 1
        return result

    def get_word_tag(self, word):
        text = word.get('text')
        tag = word.get('tag')
        data = word.get('data', [])
        index = word.get('index')
        return self._el('text', {
            'classnames': ['displacy-token'],
            'attributes': [
                ['fill', 'currentColor'],
                ['data-tag', tag],
                ['text-anchor', 'middle'],
                ['y', str(self.offset_y + self.word_spacing)],
            ] + self.get_data_attributes(data),
            'children': [
                self._el('tspan', {
                    'classnames': ['displacy-word'],
                    'attributes': [
                        ['x', str(self.offset_x + index * self.word_distance)],
                        ['fill', 'currentColor'],
                        ['data-tag', tag],
                    ],
                    'text': text,
                }),
                self._el('tspan', {
                    'classnames': ['displacy-tag'],
                    'attributes': [
                        ['x', str(self.offset_x + index * self.word_distance)],
                        ['dy', '2em'],
                        ['fill', 'currentColor'],
                        ['data-tag', tag],
                    ],
                    'text': tag,
                })
            ],
        })

    def get_arrow_tag(self, arc):
        label = arc.get('label')
        end = arc.get('end')
        start = arc.get('start')
        direction = arc.get('dir')
        level = arc.get('level')
        data = arc.get('data', [])
        index = arc.get('index')
        tag_index = arc.get('tag_index')

        start_x = self.offset_x + start * self.word_distance + self.arrow_spacing * (self.highest_level - level) / 4
        start_y = self.offset_y
        endpoint = self.offset_x + (end - start) * self.word_distance + start * self.word_distance \
            - self.arrow_spacing * (self.highest_level - level) / 4

        curve = self.offset_y - level * self.arc_distance
        if curve == 0 and self.highest_level >= 5:
            curve = -self.word_distance

        aw2 = self.arrow_width - 2

        return self._el('g', {
                'classnames': ['displacy-arrow'],
                'attributes': [
                    ['data-dir', dir],
                    ['data-label', label],
                ] + self.get_data_attributes(data),
                'children': [
                    self._el('path', {
                        'id': 'arrow-' + str(tag_index) + '-' + str(index),
                        'classnames': ['displacy-arc'],
                        'attributes': [
                            ['d', 'M{},{} C{},{} {},{} {},{}'.format(
                                start_x, start_y,
                                start_x, curve,
                                endpoint, curve,
                                endpoint, start_y
                            )],
                            ['stroke-width', str(self.arrow_stroke) + 'px'],
                            ['fill', 'none'],
                            ['stroke', 'currentColor'],
                            ['data-dir', direction],
                            ['data-label', label]
                        ]
                    }),
                    self._el('text', {
                        'attributes': [
                            ['dy', '1em']
                        ],
                        'children': [
                            self._el('textPath', {
                                'xlink': '#arrow-' + str(tag_index) + '-' + str(index),
                                'classnames': ['displacy-label'],
                                'attributes': [
                                    ['startOffset', '50%'],
                                    ['fill', 'currentColor'],
                                    ['text-anchor', 'middle'],
                                    ['data-label', label],
                                    ['data-dir', direction]
                                ],
                                'text': label,
                            })
                        ]
                    }),
                    self._el('path', {
                        'classnames': ['displacy-arrowhead'],
                        'attributes': [
                            ['d', 'M{},{} L{},{} {},{}'.format(
                                start_x if direction == 'left' else endpoint, start_y + 2,
                                start_x - aw2 if direction == 'left' else endpoint + aw2, start_y - self.arrow_width,
                                start_x + aw2 if direction == 'left' else endpoint - aw2, start_y - self.arrow_width
                            )],
                            ['fill', 'currentColor'],
                            ['data-label', label],
                            ['data-dir', direction]
                        ]
                    })
                ]
            })

    @staticmethod
    def _el(tag, options):
        el = ETree.Element(tag)
        attributes = options.get('attributes', [])
        if 'classnames' in options:
            attributes.append(['class', ' '.join(options['classnames'])])
        if 'style' in options:
            styles = []
            for style in options['style']:
                styles.append(': '.join(style))
            attributes.append(['style', '; '.join(styles)])
        if 'xlink' in options:
            attributes.append(['xlink:href', options['xlink']])
        if 'text' in options:
            el.text = options['text']
        if 'id' in options:
            attributes.append(['id', options['id']])

        for attribute in attributes:
            key, value = attribute
            el.set(key, str(value))
        if 'children' in options:
            el.extend(options['children'])
        return el


def main():
    nlp = spacy.load('en')
    doc = nlp('Visualise spaCy\'s guess at the syntactic structure of a sentence. '
              'Arrows point from children to heads, and are labelled by their relation type.')
    Displacy.collapse_doc(doc)
    d = Displacy({'wordDistance': 130, 'arcDistance': 40, 'wordSpacing': 30, 'arrowSpacing': 10})
    print(d.render(Displacy.words_and_arcs(doc)))


if __name__ == '__main__':
    main()
