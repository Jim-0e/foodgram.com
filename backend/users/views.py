"""Views.py."""


from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from foods.models import Follow
from foods.serializers import (FollowSerializer, SubscribeSerializer,
                               UserViewSerializer)

User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    """ViewSet пользователей."""

    queryset = User.objects.all()
    serializer_class = UserViewSerializer
    permission_classes = []

    def get_queryset(self):
        """Получение списка пользователей."""
        return User.objects.all()

    def get_permissions(self):
        """Разграничение ограничений."""
        return []

    @action(detail=True,
            url_path='me/avatar',
            methods=['put'],
            permission_classes=[IsAuthenticated])
    def avatar(self, request):
        """Добавление аватара."""
        user = request.user
        serializer = UserViewSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        """Сохранение имени и фамилии ползователя."""
        user = serializer.save()
        user.first_name = self.request.data.get('first_name')
        user.last_name = self.request.data.get('last_name')
        user.save()
        return user

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        """Получение профиля."""
        user = self.request.user
        serializer = UserViewSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(["post"],
            detail=False,
            permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        """Изменение пароля."""
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request})
        if serializer.is_valid(raise_exception=True):
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response('Пароль успешно изменен',
                            status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'],
            )
    def subscribe(self, request, id=None):
        """Оформление подписки."""
        author = get_object_or_404(User, pk=id)
        user = request.user.id

        if self.request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user, 'author': author.id},
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not Follow.objects.filter(user=request.user,
                                         author=author).exists():
                return Response(
                    {'errors': 'Вы не подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.get(user=user,
                               author=author.id).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['get'],
            serializer_class=FollowSerializer,
            permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        """Получение списка подписок."""
        user = self.request.user
        subscriptions = User.objects.filter(
            followed__user=user
        ).prefetch_related('recipes')
        paginated_queryset = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)
