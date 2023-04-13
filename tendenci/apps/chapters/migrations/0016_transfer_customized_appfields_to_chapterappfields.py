from django.db import migrations


def transfer_customized_appfields_to_chapterappfields(apps, schema_editor):
    CustomizedAppField = apps.get_model('chapters', 'CustomizedAppField')
    ChapterMembershipAppField = apps.get_model('chapters', 'ChapterMembershipAppField')
    ChapterMembershipChapterAppField = apps.get_model('chapters', 'ChapterMembershipChapterAppField')

    customized_app_fields = CustomizedAppField.objects.all()

    for customized_app_field in customized_app_fields:
        if not ChapterMembershipChapterAppField.objects.filter(chapter=customized_app_field.chapter).exists():
            for field in ChapterMembershipAppField.objects.all():
                ChapterMembershipChapterAppField.objects.create(
                    chapter=customized_app_field.chapter,
                    position=field.position,
                    label=field.label,
                    field_name=field.field_name,
                    required=field.required,
                    display=field.display,
                    customizable=field.customizable,
                    admin_only=field.admin_only,
                    field_type=field.field_type,
                    description=field.description,
                    help_text=field.help_text,
                    choices=field.choices,
                    default_value=field.default_value,
                    css_class=field.css_class,
                    content_type=field.content_type,
                )

        [chapter_app_field] = ChapterMembershipChapterAppField.objects.filter(
            chapter=customized_app_field.chapter,
            field_name=customized_app_field.app_field.field_name
        )[:1] or [None]
        if chapter_app_field:
            chapter_app_field.choices = customized_app_field.choices
            chapter_app_field.default_value = customized_app_field.default_value
            chapter_app_field.help_text = customized_app_field.help_text

            chapter_app_field.save()


class Migration(migrations.Migration):

    dependencies = [
        ('chapters', '0015_remove_chaptermembershipchapterappfield_membership_app'),
    ]

    operations = [
        migrations.RunPython(
            code=transfer_customized_appfields_to_chapterappfields,
            elidable=False
        ),
    ]
