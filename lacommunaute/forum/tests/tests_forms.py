from lacommunaute.forum.factories import CategoryForumFactory, ForumFactory
from lacommunaute.forum.forms import ForumForm, SubCategoryForumUpdateForm
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


def test_subcategoryforumupdateform():
    form = SubCategoryForumUpdateForm()
    assert form.Meta.model == Forum
    assert form.Meta.fields == ["name", "short_description", "description", "image", "certified", "partner", "parent"]
    assert form.fields["name"].required
    assert form.fields["short_description"].required
    assert not form.fields["description"].required
    assert not form.fields["image"].required
    assert not form.fields["certified"].required
    assert not form.fields["partner"].required
    assert not form.fields["tags"].required
    assert not form.fields["new_tags"].required
    assert not form.fields["parent"].required


def test_subcategoryforumupdateform_parent(db):
    form = SubCategoryForumUpdateForm()

    for parent in CategoryForumFactory.create_batch(2):
        assert parent in form.fields["parent"].queryset

    for not_parent in [
        ForumFactory(),
        CategoryForumFactory(with_child=True).get_children().first(),
        CategoryForumFactory(parent=ForumFactory()),
    ]:
        assert not_parent not in form.fields["parent"].queryset
