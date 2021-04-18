import unittest, re
from string import ascii_letters
from simple_atm_controller.exceptions import InvalidAccountId, InvalidValidationRule
from simple_atm_controller.account_id import AccountId, AccountIdValidationRule
from simple_atm_controller.pin_number import PinNumber


class AccountIdTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.pin_number = PinNumber("0000-0001")

    def test_allocate_account_id(self):
        account_id = AccountId(self.pin_number, "IML")
        self.assertEqual(account_id.pin_number, "0000-0001")
        self.assertEqual(account_id.account_id, "IML")
        self.assertEqual(account_id.items, ("0000-0001", "IML"))

    def test_default_exception(self):
        invalid_account_ids = [
            1, .1, ["0000"], ("0000",),
            {"0000"}, {"0000":"0000"},
            # ..., Anything that isn't a string
        ]
        for account_i in invalid_account_ids:
            try:
                AccountId(self.pin_number, account_i)
                self.assertTrue(False)
            except InvalidAccountId:
                pass

    def test_custom_validation_rule(self):

        class CustomAccountRule(AccountIdValidationRule):
            def validate(self, pin_number) -> bool:
                # example valid format: 0000, 0001, ...
                return bool(re.search(r"\d{4}", pin_number))

        valid_id_list = ['{0:04d}'.format(i) for i in range(10000)]
        for valid_id_i in valid_id_list:
            AccountId(self.pin_number, valid_id_i, CustomAccountRule())

        for idx in range(len(ascii_letters)):
            try:
                AccountId(
                    self.pin_number,
                    ascii_letters[idx: idx + 4],
                    CustomAccountRule()
                )
                self.assertTrue(False)
            except InvalidAccountId:
                pass

    def test_invalid_validation_rule_exception(self):

        class GoodRule(AccountIdValidationRule):
            def validate(self, account_id) -> bool:
                return True

        class InvalidReturnRule(AccountIdValidationRule):
            def validate(self, account_id) -> bool:
                return "True"

        class NotRule:
            pass

        testcase = [
            (GoodRule(), True),
            (InvalidReturnRule(), False),
            (NotRule(), False),
        ]

        for rule, result in testcase:
            try:
                AccountId(self.pin_number, "something", rule)
                self.assertTrue(result)
            except InvalidValidationRule:
                self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
