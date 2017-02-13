# displaCy.py

displaCy.py is a NLP visualizer. It's a Python port of [displaCy.js](https://github.com/explosion/displacy).
It can be used to visualize POS relationships detected using [spaCy](https://spacy.io)'s syntactic parser.

## Using displacy.py

```python
from displacy import Displacy
import spacy

nlp = spacy.load('en')
doc = nlp('Visualise spaCy\'s guess at the syntactic structure of a sentence. '
          'Arrows point from children to heads, and are labelled by their relation type.')

Displacy.collapse_doc(doc)

d = Displacy({'wordDistance': 130,
              'arcDistance': 40,
              'wordSpacing': 30,
              'arrowSpacing': 10})
print(d.render(Displacy.words_and_arcs(doc)))
```

To use with libraries other than spaCy, see the `Displacy.words_and_arcs()` method
on what input the `render()` method expects.

The following settings are available:

| Setting | Description | Default |
| --- | --- | --- |
| **wordDistance** | distance between words in px | `200` |
| **arcDistance** | distance between arcs in px | `60` |
| **offsetX** | spacing on left side of the SVG in px | `50` |
| **arrowSpacing** | spacing between arrows in px to avoid overlaps | `20` |
| **arrowWidth** | width of arrow head in px | `10` |
| **arrowStroke** | width of arc in px | `2` |
| **wordSpacing** | spacing between words and arcs in px | `75` |
| **font** | font face for all text | `'inherit'` |
| **color** | text color, HEX, RGB or color names | `'#000000'` |
| **bg** | background color, HEX, RGB or color names | `'#ffffff'` |


## Changing the theme and colours

You can find the current theme settings in [`/assets/css/displacy.css`](assets/css/displacy.css).
All elements contained in the SVG output come with tags and data attributes and can be styled flexibly using CSS.
By default, the `currentColor` of the element is used for colouring,meaning only need to change the `color` property
in CSS.

The following classes are available:

| Class name | Description |
| --- | --- |
| **.displacy-word** | word text
| **.displacy-tag** | POS tag
| **.displacy-token** | container of word and POS tag
| **.displacy-arc** | arrow arc (without label or arrow head)
| **.displacy-label** | relation type (arrow label)
| **.displacy-arrowhead** | arrow head
| **.displacy-arrow** | container of arc, label and arrow head

Additionally, you can use these attributes as attribute selectors:

| Attribute | Value | On Element |
| --- | --- | --- |
| **data-tag** | POS tag value | `.displacy-token`, `.displacy-word`, `.displacy-tag` |
| **data-label** | relation type value | `.displacy-arrow`, `.displacy-arc`, `.displacy-arrowhead`, `.displacy-label` |
| **data-dir** | direction of arrow | `.displacy-arrow`, `.displacy-arc`, `.displacy-arrowhead`, `.displacy-label` |

Using a combination of those selectors and some basic CSS logic, you can create pretty powerful templates
to style the elements based on their role and function in the parse. Here are a few examples:

```css
/* Format all words in 12px Helvetica and grey */

.displacy-word {
    font: 12px Helvetica, Arial, sans-serif;
    color: grey;
}


/* Make all noun phrases (tags that start with "NN") green */

.displacy-tag[data-tag^="NN"] {
    color: green;
}


/* Make all right arrows red and hide their labels */

.displacy-arc[data-dir="right"],
.displacy-arrowhead[data-dir="right"] {
    color: red;
}

.displacy-label[data-dir="right"] {
    display: none;
}


/* Hide all tags for verbs (tags that start with "VB") that are NOT the base form ("VB") */

.displacy-tag[data-tag^="VB"]:not([data-tag="VB"]) {
    display: none;
}


/* Only display tags if word is hovered (with smooth transition) */

.displacy-tag {
    opacity: 0;
    transition: opacity 0.25s ease;
}

.displacy-word:hover + .displacy-tag {
    opacity: 1;
}
```

## Adding custom data attributes

displaCy lets you define custom attributes via the JSON representation of the parse on both `words` and `arcs`:

```json
"words": [
    {
        "tag": "NNS",
        "text": "Robots",
        "data": [
            [ "custom", "your value here" ],
            [ "example", "example text here" ]
        ]
    }
]
```

Custom attributes are added as data attributes prefixed with `data-`, so their names shouldn't contain spaces
or special characters. If added to `words`, the data attributes are attached to the token (`.displacy-token`),
if added to `arcs`, they're attached to the arrow (`.displacy-arrow`):

```html
<text class="displacy-token" data-custom="your value here" data-example="example text here">...</text>
```
