from django import forms
from .models.building_model import Building

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = [
            'location', 'name', 'address', 'construction_year',
            'type_of_use', 'tags', 'description', 'image_urls',
            'timeline', 'active', 'audioguides'
        ]

    # def clean_location(self):
    #     return self.clean_json_field('location', required_keys=['type', 'coordinates'])
    #
    # def clean_tags(self):
    #     return self.clean_json_field('tags')
    #
    # def clean_image_urls(self):
    #     return self.clean_json_field('image_urls', image_url_validation=True)
    #
    # def clean_timeline(self):
    #     return self.clean_json_field('timeline', timeline_validation=True)