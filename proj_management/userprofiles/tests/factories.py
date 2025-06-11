import factory
from factory import fuzzy
from ..models import User, UserProfile
from factory.django import DjangoModelFactory


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile
        django_get_or_create = ('bsd_id', )

    user = factory.SubFactory('userprofiles.tests.factories.UserFactory',
                              username=factory.SelfAttribute('..bsd_id'),
                              userprofile=None)
    bsd_id = factory.Sequence(lambda n: f'bsdid{n}')
    user_level = fuzzy.FuzzyChoice(UserProfile.USER_LEVEL_CHOICES, getter=lambda c: c[0])


class UserFactory(DjangoModelFactory):
    """
    Creates a standard active user
    """
    class Meta:
        model = User
        django_get_or_create = ('username', )

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')

    username = factory.Sequence(lambda n: 'user%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
    is_active = True
    is_staff = False
    is_superuser = False

    userprofile = factory.RelatedFactory(UserProfileFactory, 'user',
                                         bsd_id=factory.SelfAttribute('..username'))








