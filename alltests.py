from pptx import Presentation
from pptx.util import Inches

prs=Presentation()

prs.slide_width = Inches(16)
prs.slide_height = Inches(9)

lyt = prs.slide_layouts[0] # choosing a slide layout
slide = prs.slides.add_slide(lyt) # adding a slide
title = slide.shapes.title # assigning a title
subtitle = slide.placeholders[1] # placeholder for subtitle
title.text = "Hey,This is a Slide! How exciting!" # title
subtitle.text = "Really?" #subtitle
prs.save("slide1.pptx") #saving file