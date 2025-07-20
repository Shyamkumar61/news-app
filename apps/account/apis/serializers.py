from rest_framework import serializers
from apps.account.utils import generate_user
from apps.account.models import Account


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(max_length=100, required=True,
                                   style={'input_type': 'email'}, write_only=True)
    password = serializers.CharField(max_length=100, required=True,
                                     style={'input_type': 'password'}, write_only=True)


class AccountSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(max_length=100, required=True,
                                             write_only=True,
                                             style={'input_type': 'password'})

    password = serializers.CharField(max_length=100, required=True, write_only=True,)

    class Meta:
        model = Account
        fields = (
            "email", "first_name", "last_name", "password", "confirm_password",
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        validated_data['username'] = generate_user()
        return Account.objects.create(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = (
            "email", "first_name", "last_name", "username",
        )