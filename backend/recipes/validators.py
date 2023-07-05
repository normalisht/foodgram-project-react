from rest_framework import serializers


class UniqueAttrValidator:
    def __init__(self, queryset, field, attrs, message=None):
        self.queryset = queryset
        self.field = field
        self.attrs = attrs.split('__')
        self.message = message

    def __call__(self, data):
        all_values = []

        for element in data[self.field]:
            for attr in self.attrs:
                element = element.get(attr)
            all_values.append(element)

        if len(all_values) > len(set(all_values)):
            raise serializers.ValidationError(
                self.message
                or f'Field {self.field} has duplicate '
                   f'values {"__".join(self.attrs)}'
            )
