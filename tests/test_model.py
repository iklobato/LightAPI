from lightapi.models import Person, Company


def test_create_person():
    """
    Test creation of a Person instance and
     verifies the Person instance is correctly created with the expected attributes.

    """
    person = Person(name="Henrique Martelini", email="henriquezmartelini@hotmail.com.com", email_verified=True)
    assert person.name == "Henrique Martelini"
    assert person.email == "henriquezmartelini@hotmail.com"
    assert person.email_verified is True
    assert person.pk is None


def test_create_company():
    company = Company(name="Iktech", email="contato@iktech.solutions", website="https://iktech.com")
    assert company.name == "Iktech"
    assert company.email == "contato@iktech.solutions"
    assert company.website == "https://iktech.com"
    assert company.pk is None