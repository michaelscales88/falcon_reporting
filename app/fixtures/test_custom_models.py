from app.fixtures.base_test import BaseTest
from app.models.custom_model import custom_model


class TestCustomModel(BaseTest):

    def setUp(self):
        super().setUp()
        self.model = custom_model('sla_report')  # This appears to be working. Need many more mixins

    def test_columns(self):
        print(self.model)
        print(self.model.__table__.columns.keys())
        self.assertTrue(True)
