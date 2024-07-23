import re
from datetime import datetime

from core.utils.enums import FloatPattern, IntegerPattern, NIDPattern, NoSymbolsPattern
from core.utils.exceptions import ValidationError


class Validators:
    @classmethod
    def required(self, allow_empty_string=False):
        def validator(value, fail_message=None):
            if value is None or (not allow_empty_string and value == ""):
                raise ValidationError(fail_message or 'value is required', 'required')
            return True

        return validator

    @classmethod
    def isIn(self, collection):
        def validator(value, fail_message=None):
            if value is not None:
                if value not in collection:
                    raise ValidationError(
                        fail_message
                        or 'value must be in {collection}'.format(
                            collection=collection
                        ),
                        'isin',
                    )
                return True

        return validator

    @classmethod
    def isNotIn(self, collection):
        def validator(value, fail_message=None):
            if value is not None:
                if value in collection:
                    raise ValidationError(
                        fail_message
                        or 'value must be in {collection}'.format(
                            collection=collection
                        ),
                        'isnotin',
                    )
                return True

        return validator

    @classmethod
    def min(self, min):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if not float(value) >= min:
                    raise ValidationError(
                        fail_message
                        or 'value must be greater than {min}'.format(min=min),
                        'gte',
                    )
                return True

        return validator

    @classmethod
    def max(self, max):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if not float(value) <= max:
                    raise ValidationError(
                        fail_message or 'value must be less than {max}'.format(max=max),
                        'lte',
                    )
                return True

        return validator

    @classmethod
    def equal(self, compare):
        def validator(value, fail_message=None):
            if compare and value is not None and value != "":
                if not value == compare:
                    raise ValidationError(
                        fail_message
                        or 'value must be equal {compare}'.format(compare=compare),
                        'equal',
                    )
                return True

        return validator

    @classmethod
    def notEqual(self, compare):
        def validator(value, fail_message=None):
            if compare and value is not None and value != "":
                if value == compare:
                    raise ValidationError(
                        fail_message
                        or 'value must not equal {compare}'.format(compare=compare),
                        'notEqual',
                    )
                return True

        return validator

    @classmethod
    def equalLength(self, equal):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if isinstance(value, int) or isinstance(value, float):
                    value = str(value)
                if not len(value) == equal:
                    raise ValidationError(
                        fail_message
                        or 'value length must be equal {equal}'.format(equal=equal),
                        'gte',
                    )
                return True

        return validator

    @classmethod
    def minLength(self, min):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if isinstance(value, int) or isinstance(value, float):
                    value = str(value)
                if not len(value) >= min:
                    raise ValidationError(
                        fail_message
                        or 'value length must be greater than {min}'.format(min=min),
                        'gte',
                    )
                return True

        return validator

    @classmethod
    def maxLength(self, max):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if isinstance(value, int) or isinstance(value, float):
                    value = str(value)
                if not len(value) <= max:
                    raise ValidationError(
                        fail_message
                        or 'value length must be less than {max}'.format(max=max),
                        'lte',
                    )
                return True

        return validator

    @classmethod
    def minDate(self, min):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if isinstance(value, str):
                    value = datetime.strptime(value, '%Y-%m-%d')
                if isinstance(value, datetime) and not value >= min:
                    raise ValidationError(
                        fail_message
                        or 'value date must be greater than {min}'.format(min=min),
                        'lte_date',
                    )
                return True

        return validator

    @classmethod
    def maxDate(self, max):
        def validator(value, fail_message=None):
            if value is not None and value != "":
                if isinstance(value, str):
                    value = datetime.strptime(value, '%Y-%m-%d')
                if isinstance(value, datetime) and not value <= max:
                    raise ValidationError(
                        fail_message
                        or 'value date  must be less than {max}'.format(max=max),
                        'lte',
                    )
                return True

        return validator

    @classmethod
    def regex(self, regex_format):
        def validator(value, fail_message=None):
            if value is not None:
                if isinstance(value, str):
                    if value != "" and not re.search(regex_format, value):
                        raise ValidationError(
                            fail_message or 'value does not match the expected format',
                            'match',
                        )
                else:
                    raise ValidationError(
                        'value of {} type cannot be tested for '
                        'format'.format(type(value).__name__),
                        'match',
                    )
                return True

        return validator

    @classmethod
    def isInteger(self):
        def validator(value, fail_message=None):
            if value is not None:
                if isinstance(value, int):
                    return True
                if isinstance(value, float):
                    raise ValidationError(
                        fail_message
                        or 'value does not match the expected integer format',
                        'match',
                    )
                if isinstance(value, str):
                    if value != "" and not re.search(IntegerPattern, value):
                        raise ValidationError(
                            fail_message
                            or 'value does not match the expected integer format',
                            'match',
                        )
                else:
                    raise ValidationError(
                        'value of {} type cannot be tested for '
                        'format'.format(type(value).__name__),
                        'match',
                    )
                return True

        return validator

    @classmethod
    def isFloat(self):
        def validator(value, fail_message=None):
            if value is not None:
                if isinstance(value, float) or isinstance(value, int):
                    return True
                if isinstance(value, str):
                    if value != "" and not re.search(FloatPattern, value):
                        raise ValidationError(
                            fail_message
                            or 'value does not match the expected float format',
                            'match',
                        )
                else:
                    raise ValidationError(
                        'value of {} type cannot be tested for '
                        'format'.format(type(value).__name__),
                        'match',
                    )
                return True

        return validator

    @classmethod
    def isNationalID(self):
        def validator(value, fail_message=None):
            if value is not None:
                if isinstance(value, int):
                    value = str(value)
                try:
                    if not re.search(NIDPattern, value):
                        raise ValidationError(
                            fail_message
                            or 'value does not match the expected national ID format',
                            'match',
                        )
                except TypeError:
                    raise ValidationError(
                        'value of {} type cannot be tested for '
                        'format'.format(type(value).__name__),
                        'match',
                    )
                return True

        return validator

    @classmethod
    def isLettersOnly(self):
        return Validators.regex(NoSymbolsPattern)


class Validation:
    @classmethod
    def run_validator(
        self, validator, value, fail_message=None, supress_exceptions=False
    ):
        try:
            validator(value, fail_message)
            return True
        except ValidationError:
            if supress_exceptions:
                return False
            raise

    @classmethod
    def run_validators_set(self, validator_set, supress_exceptions=False):
        try:
            for instance in validator_set:
                validator = instance[0]
                value = instance[1]
                fail_message = instance[2] if len(instance) > 2 else None
                validator(value, fail_message)
            return {'success': True}
        except ValidationError as ex:
            if supress_exceptions:
                return {'success': False, 'message': str(ex)}
            raise

    @classmethod
    def run_all_validators(self, validator_set):
        errors = []
        for instance in validator_set:
            validator = instance[0]
            value = instance[1]
            fail_message = instance[2] if len(instance) > 2 else None
            try:
                validator(value, fail_message)
            except ValidationError:
                errors.append(fail_message)
        return {'success': not bool(errors), 'errors': errors}
