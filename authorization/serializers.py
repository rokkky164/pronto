from rest_framework import serializers

from authorization.models import Permission, Role, AccountVerificationRequest


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = ('id', 'keyword', )


class RoleListSerializer(serializers.ModelSerializer):
    role_type = serializers.SlugRelatedField('role_type.name', read_only=True)

    class Meta:
        model = Role
        fields = ('id', 'name', 'label', 'role_type', )


class RoleShortDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'label',)


class RoleDetailSerializer(serializers.ModelSerializer):
    role_type = serializers.SlugRelatedField('role_type.name', read_only=True)
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Role
        fields = ('id', 'name', 'label', 'role_type', 'permissions', )


class PartialRoleUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'label',)


class RoleUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = ('id', 'name', 'label', )


class AccountVerificationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = AccountVerificationRequest
        fields = '__all__'
