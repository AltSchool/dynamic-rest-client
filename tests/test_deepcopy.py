from __future__ import absolute_import
from tests.models import (
    Cat,
    Location,
)
import copy

from rest_framework.test import APITestCase


class DeepcopyTestCase(APITestCase):
    def test_cat(self):
        home = Location(name='Home', blob='ILUVU')
        papa = Cat(name='Papa')
        kitkat = Cat(name='KitKat', home=home, parent=papa)
        kitkat_clone = copy.deepcopy(kitkat)

        self.assertEquals(kitkat.name, kitkat_clone.name)
        self.assertEquals(kitkat.home.name, kitkat_clone.home.name)
        self.assertEquals(kitkat.parent.name, kitkat_clone.parent.name)
