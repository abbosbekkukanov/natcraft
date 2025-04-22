from modeltranslation.translator import register, TranslationOptions
from .models import Banner, AboutUs, OurTeam, Craftsmanship, Craftsmanshiplist, CraftsmanshipFeature, FeatureItem, SocialMediaLink

@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('name', 'text', 'author')

@register(AboutUs)
class AboutUsTranslationOptions(TranslationOptions):
    fields = ('title', 'mission', 'history')

@register(OurTeam)
class OurTeamTranslationOptions(TranslationOptions):
    fields = ('name', 'text', 'profession')

@register(Craftsmanship)
class CraftsmanshipTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

@register(Craftsmanshiplist)
class CraftsmanshiplistTranslationOptions(TranslationOptions):
    fields = ('title', 'text')

@register(CraftsmanshipFeature)
class CraftsmanshipFeatureTranslationOptions(TranslationOptions):
    fields = ('key',)

@register(FeatureItem)
class FeatureItemTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(SocialMediaLink)
class SocialMediaLinkTranslationOptions(TranslationOptions):
    fields = ('name',)