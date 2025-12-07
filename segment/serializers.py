from rest_framework import serializers
from django.conf import settings

class CaptureSerializer(serializers.Serializer):
    rgb_url = serializers.SerializerMethodField()
    depth_csv_url = serializers.SerializerMethodField()

    def __init__(self, rgb_path, depth_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rgb_path = rgb_path
        self.depth_path = depth_path

    def get_rgb_url(self, obj=None):
        return f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}{self.rgb_path}"

    def get_depth_csv_url(self, obj=None):
        return f"{settings.PUBLIC_DOMAIN}{settings.MEDIA_URL}{self.depth_path}"
