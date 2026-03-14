import json
import os
from datetime import datetime

class ScriptureSlide:
    """Represents a single scripture slide entry."""
    def __init__(self, ref, text, screens):
        self.ref = ref
        self.text = text
        self.screens = screens  # e.g. ['left_pillar', 'right_pillar', 'banner']

    def to_dict(self):
        return {
            'ref': self.ref,
            'text': self.text,
            'screens': self.screens
        }


class ProGenerator:
    """
    Generates a ProPresenter 7 file from a list of ScriptureSlides.

    Currently outputs a structured JSON placeholder.
    When proto definitions are available, replace the `build_pro_file`
    method with real protobuf generation — everything else stays the same.
    """

    def __init__(self, slides, output_path):
        self.slides = slides          # list of ScriptureSlide objects
        self.output_path = output_path

    def build_slide(self, slide):
        """
        Build a single slide structure.

        TODO: Replace this with real protobuf slide construction
        once we have the decoded template slide from the church computer.
        """
        return {
            'type': 'scripture_slide',
            'ref': slide.ref,
            'text': slide.text,
            'screens': slide.screens,
            'layout': 'default_template',  # will reference the real template UUID
            'text_box': {
                'position': 'TBD',          # will come from decoded template
                'font': 'TBD',
                'font_size': 'TBD',
                'color': 'TBD'
            }
        }

    def build_pro_file(self):
        """
        Assembles all slides into a presentation structure.

        TODO: Replace JSON output with protobuf binary (.pro file)
        once proto definitions are compiled.
        """
        presentation = {
            'meta': {
                'generated_by': 'Scripture Builder',
                'generated_at': datetime.now().isoformat(),
                'slide_count': len(self.slides)
            },
            'slides': [self.build_slide(s) for s in self.slides]
        }
        return presentation

    def save(self):
        """Save the presentation to the output path."""
        presentation = self.build_pro_file()

        # TODO: When real proto generation is ready, this becomes:
        # with open(self.output_path, 'wb') as f:
        #     f.write(presentation.SerializeToString())

        # For now, save as JSON so we can inspect the structure
        json_path = self.output_path.replace('.pro', '_preview.json')
        with open(json_path, 'w') as f:
            json.dump(presentation, f, indent=2)

        print(f'Saved preview to: {json_path}')
        return json_path