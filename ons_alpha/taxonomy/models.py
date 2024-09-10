from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from treebeard.mp_tree import MP_Node
from wagtail.admin.forms import WagtailAdminModelForm
from wagtail.admin.panels import FieldPanel
from wagtail.models import Orderable
from wagtail.search import index


# This is the main 'node' model, it inherits mp_node
# mp_node is short for materialized path, it means the tree has a clear path
class Topic(index.Indexed, MP_Node):
    name = models.CharField(max_length=100)

    node_order_by = ["name"]

    panels = [
        FieldPanel("name", classname="full"),
        FieldPanel(
            "parent", help_text="Where this topic will be nested under. Leave blank for top-level topics."
        ),  # parent is not a field on the model, it is built in the TopicForm form class
    ]

    search_fields = [
        index.FilterField("name"),
        index.FilterField("depth"),
        index.SearchField("name"),
        index.AutocompleteField("name"),
    ]

    def __str__(self):
        return self.name_with_depth()

    # this is just a convenience function to make the names appear with lines
    # eg root | - first child
    def name_with_depth(self):
        depth = "— " * (self.get_depth() - 1)
        return depth + self.name

    name_with_depth.short_description = "Name"

    @property
    def parent_name(self):
        if not self.is_root():
            return self.get_parent().name
        return None


# this class is the form class override for Topic
class TopicForm(WagtailAdminModelForm):
    # build a parent field that will show the available topics
    parent = forms.ModelChoiceField(
        required=False,
        empty_label="None",
        queryset=Topic.objects.none(),
        label="Parent Topic",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs["instance"]

        if instance:
            self.fields["parent"].queryset = Topic.objects.exclude(pk=instance.pk)
            self.fields["parent"].initial = instance.get_parent()

        else:
            self.fields["parent"].queryset = Topic.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get("parent")
        instance = self.instance

        if not parent and instance.get_parent() != parent:
            raise ValidationError("Cannot make a child topic a top-level topic.")

        # depth starts with one. We cannot rely on instance.get_parent()
        # until after the topic is created, and parent can be None
        depth = parent.depth + 1 if parent else 1
        if Topic.objects.filter(name=cleaned_data["name"], depth=depth).exists():
            raise ValidationError("A topic with this name already exists.")

        return cleaned_data

    def save(self, commit=True):
        parent = self.cleaned_data["parent"]
        instance = super().save(commit=False)

        if not commit:
            return instance

        if instance.id is None:
            instance = parent.add_child(instance=instance) if parent else Topic.add_root(instance=instance)
        elif instance.get_parent() != parent:
            instance.move(parent, pos="sorted-child")
        else:
            instance.save()

        return instance


# use our form class override
Topic.base_form_class = TopicForm


class PageTopicRelationship(Orderable):
    page = ParentalKey("wagtailcore.Page", on_delete=models.CASCADE, related_name="topics")
    topic = models.ForeignKey("taxonomy.Topic", on_delete=models.CASCADE, related_name="related_pages")
