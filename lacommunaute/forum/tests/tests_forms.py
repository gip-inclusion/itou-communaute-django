import pytest  # noqa

from lacommunaute.forum.forms import wrap_iframe_in_div_tag

from lacommunaute.forum.forms import ForumForm
from lacommunaute.forum.models import Forum


def test_wrap_iframe_in_div_tag():
    inputs = [
        "<iframe src='xxx'></iframe>",
        "<div><iframe src='yyy'></iframe></div>",
        "<div><iframe src='zzz'></iframe>",
        "<iframe src='www'></iframe></div>",
    ]
    outputs = [
        "<div><iframe src='xxx'></iframe></div>",
        "<div><iframe src='yyy'></iframe></div>",
        "<div><iframe src='zzz'></iframe>",
        "<iframe src='www'></iframe></div>",
    ]
    assert wrap_iframe_in_div_tag(" ".join(inputs)) == " ".join(outputs)


def test_saved_forum_description(db):
    form = ForumForm(
        data={
            "name": "test",
            "short_description": "test",
            "description": "Text\n<iframe src='xxx'></iframe>\ntext\n<div><iframe src='yyy'></iframe></div>\nbye",
        }
    )
    assert form.is_valid()
    form.instance.type = Forum.FORUM_POST
    forum = form.save()
    assert forum.description.rendered == (
        "<p>Text</p>\n\n<div><iframe src='xxx'></iframe></div>\n\n"
        "<p>text</p>\n\n<div><iframe src='yyy'></iframe></div>\n\n<p>bye</p>"
    )


def test_form_field():
    form = ForumForm()
    assert form.Meta.model == Forum
    assert form.Meta.fields == ["name", "short_description", "description", "image", "certified", "partner"]
    assert form.fields["name"].required
    assert form.fields["short_description"].required
    assert not form.fields["description"].required
    assert not form.fields["image"].required
    assert not form.fields["certified"].required
    assert not form.fields["partner"].required
    assert not form.fields["tags"].required
    assert not form.fields["new_tags"].required
