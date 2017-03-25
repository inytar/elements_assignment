from rest_framework import renderers

class ImageRenderer(renderers.BaseRenderer):
    media_type = 'image/*'
    format = 'image'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type, renderer_context=None):
        return data
