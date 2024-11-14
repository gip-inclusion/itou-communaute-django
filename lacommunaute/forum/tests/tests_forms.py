from lacommunaute.forum.forms import ForumForm
from lacommunaute.forum.models import Forum


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
